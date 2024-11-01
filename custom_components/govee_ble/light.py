import logging
import pygatt
from datetime import timedelta

from homeassistant.components.light import (
    LightEntity, SUPPORT_BRIGHTNESS, SUPPORT_COLOR
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_BRIGHTNESS, DEFAULT_RGB_COLOR

_LOGGER = logging.getLogger(__name__)

RETRY_LIMIT = 3
KEEP_ALIVE_INTERVAL = 60  # seconds
STATE_SYNC_INTERVAL = 300  # seconds, for state verification

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Smart Light from a config entry."""
    mac_address = entry.data["mac_address"]
    name = entry.data.get("name", DEFAULT_NAME)
    initial_brightness = entry.data.get("initial_brightness", DEFAULT_BRIGHTNESS)
    initial_color = entry.data.get("initial_color", DEFAULT_RGB_COLOR)
    async_add_entities([SmartLight(mac_address, name, initial_brightness, initial_color)])

class SmartLight(LightEntity):
    def __init__(self, mac_address, name, initial_brightness, initial_color):
        self._mac_address = mac_address
        self._name = name
        self._brightness = initial_brightness
        self._rgb_color = initial_color
        self._state = False
        self._adapter = pygatt.backends.GATTToolBackend()
        self._keep_alive_unsub = None
        self._sync_state_unsub = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR

    def turn_on(self, **kwargs):
        self._state = True
        if 'brightness' in kwargs:
            self.set_brightness(kwargs['brightness'])
        if 'rgb_color' in kwargs:
            self.set_rgb_color(kwargs['rgb_color'])
        else:
            self.set_brightness(self._brightness)
            self.set_rgb_color(self._rgb_color)

        self._send_command([0x33, 0x01, 0x01] + [0x00] * 16)

    def turn_off(self, **kwargs):
        self._state = False
        self._send_command([0x33, 0x01, 0x00] + [0x00] * 16)

    async def async_added_to_hass(self):
        """Initialize the smart light state and setup intervals."""
        @callback
        def keep_alive(now):
            """Send keep-alive packet to maintain the connection."""
            keep_alive_packet = [0xAA, 0x01] + [0x00] * 17
            checksum = self._calculate_checksum(keep_alive_packet)
            keep_alive_packet.append(checksum)
            self._send_command(keep_alive_packet)

        @callback
        def sync_state(now):
            """Synchronize the state with the actual device status."""
            # Placeholder for state retrieval and update logic
            # This would involve reading from the device and setting
            # self._state, self._brightness, and self._rgb_color

        self._keep_alive_unsub = async_track_time_interval(
            self.hass, keep_alive, timedelta(seconds=KEEP_ALIVE_INTERVAL)
        )

        self._sync_state_unsub = async_track_time_interval(
            self.hass, sync_state, timedelta(seconds=STATE_SYNC_INTERVAL)
        )

    async def async_will_remove_from_hass(self):
        """Clean up before entity removal."""
        if self._keep_alive_unsub:
            self._keep_alive_unsub()
            self._keep_alive_unsub = None

        if self._sync_state_unsub:
            self._sync_state_unsub()
            self._sync_state_unsub = None

    def set_brightness(self, brightness):
        self._brightness = brightness
        command = [0x33, 0x04, brightness] + [0x00] * 16
        command.append(self._calculate_checksum(command))
        self._send_command(command)

    def set_rgb_color(self, rgb_color):
        self._rgb_color = rgb_color
        r, g, b = rgb_color
        command = [0x33, 0x05, 0x02, r, g, b] + [0x00] * 13
        command.append(self._calculate_checksum(command))
        self._send_command(command)

    def _send_command(self, command):
        self._adapter.start()
        attempt = 0
        successful = False

        while attempt < RETRY_LIMIT and not successful:
            try:
                device = self._adapter.connect(self._mac_address)
                device.char_write('00010203-0405-0607-0809-0a0b0c0d2b11', bytearray(command))
                successful = True
            except pygatt.exceptions.BLEError as e:
                attempt += 1
                _LOGGER.error(f"Attempt {attempt}: Error communicating with smart light - {e}")
                if attempt >= RETRY_LIMIT:
                    _LOGGER.error("Max retry limit reached. Could not send command.")
            finally:
                self._adapter.stop()

    @staticmethod
    def _calculate_checksum(packet):
        checksum = 0
        for byte in packet:
            checksum ^= byte
        return checksum