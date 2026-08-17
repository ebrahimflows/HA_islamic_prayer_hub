"""Config flow for Prayer Hub."""

from __future__ import annotations

import secrets
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
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
    DEFAULT_VIDEO_ID,
    DEFAULT_FAJR_VIDEO_ID,
    DEFAULT_VOLUME,
    DEFAULT_COUNTDOWN,
    DEFAULT_FALLBACK_SECONDS,
    DEFAULT_DASHBOARD_PATH,
)


class PrayerHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Prayer Hub setup."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Set up Prayer Hub."""
        lupt_entities = sorted(
            state.entity_id for state in self.hass.states.async_all("lupt")
        )

        if not lupt_entities:
            return self.async_abort(reason="lupt_not_found")

        if user_input is not None:
            await self.async_set_unique_id("prayer_hub")
            self._abort_if_unique_id_configured()
            user_input[CONF_FINISH_TOKEN] = secrets.token_urlsafe(32)
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, "Prayer Hub"),
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default="Prayer Hub"): str,
                vol.Required(CONF_LUPT_ENTITY, default=lupt_entities[0]): vol.In(lupt_entities),
                vol.Required(CONF_TV_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="media_player")
                ),
                vol.Required(CONF_TABLET_SCREEN_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_FULLY_KIOSK_DEVICE_ID): str,
                vol.Required(
                    CONF_HOME_ASSISTANT_URL,
                    default=(
                        self.hass.config.internal_url
                        or self.hass.config.external_url
                        or "http://homeassistant.local:8123"
                    ),
                ): str,
                vol.Optional(
                    CONF_DASHBOARD_RETURN_PATH,
                    default=DEFAULT_DASHBOARD_PATH,
                ): str,
                vol.Required(CONF_LIGHT_ENTITIES): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
                vol.Optional(CONF_VIDEO_ID, default=DEFAULT_VIDEO_ID): str,
                vol.Optional(CONF_FAJR_VIDEO_ID, default=DEFAULT_FAJR_VIDEO_ID): str,
                vol.Optional(CONF_VOLUME, default=DEFAULT_VOLUME): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=100)
                ),
                vol.Optional(CONF_COUNTDOWN, default=DEFAULT_COUNTDOWN): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=30)
                ),
                vol.Optional(
                    CONF_FALLBACK_SECONDS,
                    default=DEFAULT_FALLBACK_SECONDS,
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=1800)),
                vol.Optional(CONF_AUTOMATIC, default=True): bool,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)
