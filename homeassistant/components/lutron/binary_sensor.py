"""Support for Lutron Powr Savr occupancy sensors."""
from pylutron import OccupancyGroup

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
)

from . import LUTRON_CONTROLLER, LUTRON_DEVICES, LutronDevice
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up occupancy sensors for a Lutron deployment."""
    async_add_entities(
        LutronOccupancySensor(
            suggested_area,
            device,
            hass.data[DOMAIN][entry.entry_id][LUTRON_CONTROLLER],
        )
        for (suggested_area, device) in hass.data[DOMAIN][entry.entry_id][
            LUTRON_DEVICES
        ]["binary_sensor"]
    )


class LutronOccupancySensor(LutronDevice, BinarySensorEntity):
    """Representation of a Lutron Occupancy Group.

    The Lutron integration API reports "occupancy groups" rather than
    individual sensors. If two sensors are in the same room, they're
    reported as a single occupancy group.
    """

    _attr_device_class = DEVICE_CLASS_OCCUPANCY

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        # Error cases will end up treated as unoccupied.
        return self._lutron_device.state == OccupancyGroup.State.OCCUPIED

    @property
    def name(self):
        """Return the name of the device."""
        # The default LutronDevice naming would create 'Kitchen Occ Kitchen',
        # but since there can only be one OccupancyGroup per area we go
        # with something shorter.
        return f"{self._suggested_area} Occupancy"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"lutron_integration_id": self._lutron_device.id}
