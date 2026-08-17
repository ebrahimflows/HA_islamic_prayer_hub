"""Prayer Hub data coordinator."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import NEXT_ATTRIBUTE_MAP

_LOGGER = logging.getLogger(__name__)


class PrayerHubCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Build Prayer Hub state from the LUPT entity."""

    def __init__(self, hass: HomeAssistant, lupt_entity_id: str) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Prayer Hub",
            update_interval=timedelta(seconds=30),
        )
        self.lupt_entity_id = lupt_entity_id
        self.last_prayer = ""

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value in (None, "", "unknown", "unavailable"):
            return None
        if isinstance(value, datetime):
            result = value
        else:
            result = dt_util.parse_datetime(str(value))
        if result is None:
            return None
        if result.tzinfo is None:
            result = result.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        return result

    async def _async_update_data(self) -> dict[str, Any]:
        state = self.hass.states.get(self.lupt_entity_id)
        if state is None:
            return {
                "available": False,
                "current_prayer": "Unavailable",
                "next_prayer": "Unavailable",
                "next_prayer_time": None,
                "countdown_seconds": None,
                "islamic_date": "",
                "last_prayer": self.last_prayer,
            }

        now = dt_util.now()
        upcoming: list[tuple[str, datetime]] = []

        for prayer_name, attribute in NEXT_ATTRIBUTE_MAP.items():
            prayer_dt = self._parse_datetime(state.attributes.get(attribute))
            if prayer_dt is not None and prayer_dt > now:
                upcoming.append((prayer_name, prayer_dt))

        upcoming.sort(key=lambda item: item[1])
        next_name, next_time = upcoming[0] if upcoming else ("Unavailable", None)
        countdown = (
            max(0, int((next_time - now).total_seconds()))
            if next_time is not None
            else None
        )

        return {
            "available": True,
            "current_prayer": state.state,
            "next_prayer": next_name,
            "next_prayer_time": next_time,
            "countdown_seconds": countdown,
            "islamic_date": state.attributes.get("islamic_date", ""),
            "last_prayer": self.last_prayer,
        }
