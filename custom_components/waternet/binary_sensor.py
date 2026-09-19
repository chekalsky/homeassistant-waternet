"""Waternet fetch-status binary sensor."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import WaternetCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the last-update-successful binary sensor."""
    async_add_entities([WaternetUpdateSuccessSensor(entry.runtime_data)])


class WaternetUpdateSuccessSensor(
    CoordinatorEntity[WaternetCoordinator], BinarySensorEntity
):
    """On when the latest Waternet fetch succeeded."""

    _attr_has_entity_name = True
    _attr_attribution = "Data from Waternet"
    _attr_translation_key = "last_update_successful"
    _attr_unique_id = "last_update_successful"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: WaternetCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success
