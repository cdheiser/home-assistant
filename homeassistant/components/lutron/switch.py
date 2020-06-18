"""Support for Lutron switches."""
from itertools import chain

from homeassistant.components.switch import SwitchEntity

from . import LUTRON_CONTROLLER, LUTRON_DEVICES, LutronDevice
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches and leds for a Lutron deployment."""
    async_add_entities(
        chain(
            (
                LutronSwitch(
                    suggested_area,
                    device,
                    hass.data[DOMAIN][entry.entry_id][LUTRON_CONTROLLER],
                )
                for (suggested_area, device) in hass.data[DOMAIN][entry.entry_id][
                    LUTRON_DEVICES
                ]["switch"]
            ),
            (
                LutronLed(
                    suggested_area,
                    keypad,
                    device,
                    led,
                    hass.data[DOMAIN][entry.entry_id][LUTRON_CONTROLLER],
                )
                for (suggested_area, keypad, device, led) in hass.data[DOMAIN][
                    entry.entry_id
                ][LUTRON_DEVICES]["scene"]
                if led
            ),
        ),
        True,
    )


class LutronSwitch(LutronDevice, SwitchEntity):
    """Representation of a Lutron Switch."""

    def __init__(self, suggested_area, lutron_device, controller):
        """Initialize the switch."""
        self._prev_state = None
        super().__init__(suggested_area, lutron_device, controller)

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._lutron_device.level = 100

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._lutron_device.level = 0

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"lutron_integration_id": self._lutron_device.id}

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._lutron_device.last_level() > 0

    def update(self):
        """Call when forcing a refresh of the device."""
        if self._prev_state is None:
            self._prev_state = self._lutron_device.level > 0


class LutronLed(LutronDevice, SwitchEntity):
    """Representation of a Lutron Keypad LED."""

    def __init__(self, suggested_area, keypad, scene_device, led_device, controller):
        """Initialize the switch."""
        self._keypad = keypad
        self._scene_name = scene_device.name
        self._keypad_unique_id = f"{led_device._lutron.guid}_{keypad.uuid}"
        super().__init__(suggested_area, led_device, controller)

    def turn_on(self, **kwargs):
        """Turn the LED on."""
        self._lutron_device.state = 1

    def turn_off(self, **kwargs):
        """Turn the LED off."""
        self._lutron_device.state = 0

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "keypad": self._keypad_name,
            "scene": self._scene_name,
            "led": self._lutron_device.name,
        }

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._lutron_device.last_state

    @property
    def name(self):
        """Return the name of the LED."""
        return f"{self._suggested_area} {self._keypad.name}: {self._scene_name} LED"

    def update(self):
        """Call when forcing a refresh of the device."""
        if self._lutron_device.last_state is not None:
            return

        # The following property getter actually triggers an update in Lutron
        self._lutron_device.state  # pylint: disable=pointless-statement

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
            "via_device": (DOMAIN, self._controller.guid),
        }
        if self._include_areas:
            device_info["suggested_area"] = self._suggested_area
        return device_info
