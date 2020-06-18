"""Support for Lutron scenes."""
from typing import Any

from homeassistant.components.scene import Scene

from . import LUTRON_CONTROLLER, LUTRON_DEVICES, LutronDevice
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up scenes for a Lutron Deployment."""
    async_add_entities(
        (
            LutronScene(
                suggested_area,
                keypad,
                device,
                led,
                hass.data[DOMAIN][entry.entry_id][LUTRON_CONTROLLER],
            )
            for (suggested_area, keypad, device, led) in hass.data[DOMAIN][
                entry.entry_id
            ][LUTRON_DEVICES]["scene"]
        ),
        True,
    )


class LutronScene(LutronDevice, Scene):
    """Representation of a Lutron Scene."""

    def __init__(self, suggested_area, keypad, lutron_device, lutron_led, controller):
        """Initialize the scene/button."""
        self._keypad = keypad
        self._led = lutron_led
        super().__init__(suggested_area, lutron_device, controller)
        self._keypad_unique_id = f"{self._controller.guid}_{self._keypad.uuid}"

    def activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        self._lutron_device.press()

    @property
    def name(self):
        """Return the name of the device."""
        if self._include_areas:
            return f"{self._keypad.name}: {self._lutron_device.name}"
        return f"{self._suggested_area} {self._keypad.name}: {self._lutron_device.name}"

    @property
    def device_info(self):
        """Return key device information."""
        device_info = {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._keypad_unique_id)
            },
            "name": f"{self._suggested_area} {self._keypad.name}",
            "manufacturer": "Lutron",
            "model": self._keypad.type,
            # "sw_version": self.light.swversion,
            "via_device": (DOMAIN, self._lutron_device._lutron.guid),
        }
        if self._include_areas:
            device_info["suggested_area"] = self._suggested_area
        return device_info
