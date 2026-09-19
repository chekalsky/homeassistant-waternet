"""Waternet tariff sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import WaternetCoordinator


@dataclass(frozen=True, kw_only=True)
class WaternetSensorEntityDescription(SensorEntityDescription):
    """Sensor that reads a value from the coordinator."""

    value_fn: Callable[[WaternetCoordinator], datetime | float | None]


SENSORS = (
    WaternetSensorEntityDescription(
        key="price_per_liter",
        translation_key="price_per_liter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfVolume.LITERS}",
        suggested_display_precision=6,
        value_fn=lambda c: c.data.price_per_liter if c.data else None,
    ),
    WaternetSensorEntityDescription(
        key="price_per_m3",
        translation_key="price_per_m3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfVolume.CUBIC_METERS}",
        suggested_display_precision=4,
        value_fn=lambda c: c.data.price_per_m3 if c.data else None,
    ),
    WaternetSensorEntityDescription(
        key="standing_charge",
        translation_key="standing_charge",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=f"{CURRENCY_EURO}/year",
        suggested_display_precision=2,
        value_fn=lambda c: c.data.standing_charge_incl_vat if c.data else None,
    ),
    WaternetSensorEntityDescription(
        key="last_successful_fetch",
        translation_key="last_successful_fetch",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda c: c.last_update_success_time,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Waternet sensors."""
    coordinator: WaternetCoordinator = entry.runtime_data
    async_add_entities(
        WaternetSensor(coordinator, description) for description in SENSORS
    )


class WaternetSensor(CoordinatorEntity[WaternetCoordinator], SensorEntity):
    """One Waternet tariff figure."""

    entity_description: WaternetSensorEntityDescription
    _attr_has_entity_name = True
    _attr_attribution = "Data from Waternet"

    def __init__(
        self,
        coordinator: WaternetCoordinator,
        description: WaternetSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return self.coordinator.last_update_success_time is not None
        return self.coordinator.data is not None

    @property
    def native_value(self) -> datetime | float | None:
        value = self.entity_description.value_fn(self.coordinator)
        if value is None or isinstance(value, datetime):
            return value
        digits = self.entity_description.suggested_display_precision or 6
        return round(value, digits)

    @property
    def extra_state_attributes(self) -> dict[str, float | int] | None:
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return None
        data = self.coordinator.data
        if not data:
            return None
        return {
            "year": data.year,
            "water_eur_m3": data.water_eur_m3,
            "bol_eur_m3": data.bol_eur_m3,
            "vat_percent": data.vat_percent,
            "standing_charge_eur_year": data.standing_charge_eur_year,
        }
