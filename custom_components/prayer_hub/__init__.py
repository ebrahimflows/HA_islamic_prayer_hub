"""Prayer Hub private integration."""

from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_START,
    SERVICE_STOP,
    PRAYER_STATES,
    CONF_LUPT_ENTITY,
    CONF_TV_ENTITY,
    CONF_TABLET_SCREEN_ENTITY,
    CONF_FULLY_KIOSK_DEVICE_ID,
    CONF_HOME_ASSISTANT_URL,
    CONF_DASHBOARD_RETURN_PATH,
    CONF_LIGHT_ENTITIES,
    CONF_VIDEO_ID,
    CONF_FAJR_VIDEO_ID,
    CONF_VOLUME,
    CONF_COUNTDOWN,
    CONF_FALLBACK_SECONDS,
    CONF_AUTOMATIC,
    CONF_FINISH_TOKEN,
    DEFAULT_FAJR_VIDEO_ID,
)
from .coordinator import PrayerHubCoordinator

START_SCHEMA = vol.Schema(
    {
        vol.Required("prayer_name"): cv.string,
        vol.Optional("prayer_time", default=""): cv.string,
    }
)


class PrayerHubFinishView(HomeAssistantView):
    """Receive a private local finish callback from the tablet page."""

    url = "/api/prayer_hub/finish/{entry_id}/{token}"
    name = "api:prayer_hub:finish"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def post(self, request, entry_id: str, token: str):
        """Restore previous TV audio."""
        entry = self.hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            return self.json({"ok": False}, status_code=404)

        if token != entry.data.get(CONF_FINISH_TOKEN):
            return self.json({"ok": False}, status_code=403)

        peer = request.transport.get_extra_info("peername")
        remote = peer[0] if peer else ""
        if remote and not (
            remote.startswith("192.168.")
            or remote.startswith("10.")
            or remote.startswith("172.")
            or remote in ("127.0.0.1", "::1")
        ):
            return self.json({"ok": False}, status_code=403)

        runtime = self.hass.data.get(DOMAIN, {}).get(entry_id, {})
        await _async_restore_tv(self.hass, entry, runtime)
        return self.json({"ok": True})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Prayer Hub actions and callback."""
    hass.data.setdefault(DOMAIN, {})
    hass.http.register_view(PrayerHubFinishView(hass))

    async def handle_start(call: ServiceCall) -> None:
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise ValueError("Prayer Hub has not been configured.")
        entry = entries[0]
        await _async_start_prayer_hub(
            hass,
            entry,
            call.data["prayer_name"],
            call.data.get("prayer_time", ""),
        )

    async def handle_stop(call: ServiceCall) -> None:
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return
        entry = entries[0]
        runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
        await _async_restore_tv(hass, entry, runtime)

    hass.services.async_register(
        DOMAIN,
        SERVICE_START,
        handle_start,
        schema=START_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_STOP, handle_stop)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Prayer Hub from a config entry."""
    runtime = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})

    static_dir = Path(__file__).parent / "static"
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/prayer-hub", str(static_dir), False)]
    )

    coordinator = PrayerHubCoordinator(hass, entry.data[CONF_LUPT_ENTITY])
    runtime["coordinator"] = coordinator
    runtime["tv_was_on"] = False
    runtime["tv_was_muted"] = False
    runtime["last_auto_key"] = None
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    def lupt_state_changed(event) -> None:
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if old_state is None or new_state is None:
            return
        if not entry.data.get(CONF_AUTOMATIC, True):
            return
        if old_state.state == new_state.state:
            return

        prayer_name = PRAYER_STATES.get(new_state.state)
        if prayer_name is None:
            return

        now = dt_util.now()
        auto_key = f"{now.date().isoformat()}:{prayer_name}"
        if runtime.get("last_auto_key") == auto_key:
            return

        runtime["last_auto_key"] = auto_key

        attr_by_prayer = {
            "Fajr": "next_fajr",
            "Dhuhr": "next_zuhr",
            "Asr": "next_asr",
            "Maghrib": "next_maghrib",
            "Isha": "next_ishā",
        }

        scheduled_time = now.strftime("%H:%M")
        attr_name = attr_by_prayer.get(prayer_name)
        if attr_name:
            raw_value = new_state.attributes.get(attr_name)
            parsed = dt_util.parse_datetime(str(raw_value)) if raw_value else None
            if parsed is not None:
                scheduled_time = dt_util.as_local(parsed).strftime("%H:%M")

        hass.async_create_task(
            _async_start_prayer_hub(
                hass,
                entry,
                prayer_name,
                scheduled_time,
            )
        )

    runtime["unsub_lupt"] = async_track_state_change_event(
        hass,
        [entry.data[CONF_LUPT_ENTITY]],
        lupt_state_changed,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Prayer Hub."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    runtime = hass.data.get(DOMAIN, {}).pop(entry.entry_id, {})
    unsub = runtime.get("unsub_lupt")
    if unsub:
        unsub()
    return unload_ok


async def _async_start_prayer_hub(
    hass: HomeAssistant,
    entry: ConfigEntry,
    prayer_name: str,
    prayer_time: str,
) -> None:
    """Run the complete Prayer Hub sequence."""
    data = entry.data
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator: PrayerHubCoordinator = runtime["coordinator"]

    tv_entity = data[CONF_TV_ENTITY]
    tv_state = hass.states.get(tv_entity)
    runtime["tv_was_on"] = tv_state is not None and tv_state.state == "on"
    runtime["tv_was_muted"] = bool(
        tv_state.attributes.get("is_volume_muted", False)
        if tv_state is not None
        else False
    )

    if runtime["tv_was_on"]:
        await hass.services.async_call(
            "media_player",
            "volume_mute",
            {"entity_id": tv_entity, "is_volume_muted": True},
            blocking=True,
        )

    active_lights = [
        entity_id
        for entity_id in data.get(CONF_LIGHT_ENTITIES, [])
        if (state := hass.states.get(entity_id)) is not None
        and state.state == "on"
    ]

    snapshots = {}
    for entity_id in active_lights:
        state = hass.states.get(entity_id)
        attributes = state.attributes
        restore_data = {}

        if "brightness" in attributes:
            restore_data["brightness"] = attributes["brightness"]

        # Home Assistant exposes several calculated colour representations
        # simultaneously, but light.turn_on accepts only one colour descriptor.
        color_mode = attributes.get("color_mode")
        color_key_by_mode = {
            "color_temp": "color_temp_kelvin",
            "hs": "hs_color",
            "xy": "xy_color",
            "rgb": "rgb_color",
            "rgbw": "rgbw_color",
            "rgbww": "rgbww_color",
        }
        color_key = color_key_by_mode.get(color_mode)

        if color_key and attributes.get(color_key) is not None:
            restore_data[color_key] = attributes[color_key]

        snapshots[entity_id] = restore_data

    for _ in range(2):
        if not active_lights:
            break

        await hass.services.async_call(
            "light",
            "turn_off",
            {"entity_id": active_lights, "transition": 0.7},
            blocking=True,
        )
        await asyncio.sleep(0.85)

        for entity_id in active_lights:
            payload = {"entity_id": entity_id, "transition": 0.7}
            payload.update(snapshots.get(entity_id, {}))
            await hass.services.async_call(
                "light",
                "turn_on",
                payload,
                blocking=True,
            )
        await asyncio.sleep(0.85)

    await hass.services.async_call(
        "switch",
        "turn_on",
        {"entity_id": data[CONF_TABLET_SCREEN_ENTITY]},
        blocking=True,
    )
    await asyncio.sleep(0.8)

    base_url = data[CONF_HOME_ASSISTANT_URL].rstrip("/")
    finish_url = (
        f"{base_url}/api/prayer_hub/finish/"
        f"{entry.entry_id}/{data[CONF_FINISH_TOKEN]}"
    )

    if prayer_name.strip().lower() == "fajr":
        selected_video_id = data.get(CONF_FAJR_VIDEO_ID, DEFAULT_FAJR_VIDEO_ID) or DEFAULT_FAJR_VIDEO_ID
    else:
        selected_video_id = data[CONF_VIDEO_ID]

    query = urlencode(
        {
            "prayer": prayer_name,
            "time": prayer_time,
            "islamic_date": coordinator.data.get("islamic_date", ""),
            "video": selected_video_id,
            "countdown": data[CONF_COUNTDOWN],
            "volume": data[CONF_VOLUME],
            "fallback": data[CONF_FALLBACK_SECONDS],
            "return": data[CONF_DASHBOARD_RETURN_PATH],
            "webhook": finish_url,
        }
    )
    page_url = f"{base_url}/prayer-hub/index.html?{query}"

    await hass.services.async_call(
        "fully_kiosk",
        "load_url",
        {
            "device_id": data[CONF_FULLY_KIOSK_DEVICE_ID],
            "url": page_url,
        },
        blocking=True,
    )

    coordinator.last_prayer = prayer_name
    await coordinator.async_request_refresh()


async def _async_restore_tv(
    hass: HomeAssistant,
    entry: ConfigEntry,
    runtime: dict,
) -> None:
    """Restore the TV to its previous mute state."""
    if runtime.get("tv_was_on"):
        await hass.services.async_call(
            "media_player",
            "volume_mute",
            {
                "entity_id": entry.data[CONF_TV_ENTITY],
                "is_volume_muted": bool(runtime.get("tv_was_muted", False)),
            },
            blocking=True,
        )

    runtime["tv_was_on"] = False
    runtime["tv_was_muted"] = False
