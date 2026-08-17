"""Sensor platform for Prayer Hub."""

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PrayerHubCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Prayer Hub sensors."""
    coordinator: PrayerHubCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            PrayerHubTextSensor(coordinator, entry, "current_prayer", "Current Prayer", "mdi:mosque"),
            PrayerHubTextSensor(coordinator, entry, "next_prayer", "Next Prayer", "mdi:clock-outline"),
            PrayerHubDateTimeSensor(coordinator, entry),
            PrayerHubCountdownSensor(coordinator, entry),
            PrayerHubTextSensor(coordinator, entry, "islamic_date", "Islamic Date", "mdi:calendar-star"),
            PrayerHubTextSensor(coordinator, entry, "last_prayer", "Last Prayer Mode", "mdi:history"),
        ]
    )


class PrayerHubBaseSensor(CoordinatorEntity[PrayerHubCoordinator], SensorEntity):
    """Base Prayer Hub sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Prayer Hub",
            "manufacturer": "Local custom integration",
            "model": "Prayer Hub v2",
        }

    @property
    def available(self):
        return bool(self.coordinator.data.get("available", False))


class PrayerHubTextSensor(PrayerHubBaseSensor):
    """Text sensor."""

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)


class PrayerHubDateTimeSensor(PrayerHubBaseSensor):
    """Next prayer timestamp."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "next_prayer_time",
            "Next Prayer Time",
            "mdi:clock-time-four-outline",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get("next_prayer_time")


class PrayerHubCountdownSensor(PrayerHubBaseSensor):
    """Next prayer countdown."""

    _attr_native_unit_of_measurement = "s"
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "countdown_seconds",
            "Next Prayer Countdown",
            "mdi:timer-sand",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get("countdown_seconds")

    @property
    def extra_state_attributes(self):
        value = self.coordinator.data.get("countdown_seconds")
        if value is None:
            return {}
        hours, remainder = divmod(int(value), 3600)
        minutes, seconds = divmod(remainder, 60)
        return {"formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}"}
