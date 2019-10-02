#
#  Copyright (c) 2017, William Scanlon
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The pfSense/OPNsense Device Tracker API.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-pfsense/
"""

import asyncio
import logging
from typing import List

from homeassistant.components.device_tracker import DeviceScanner
from homeassistant.components.http import HomeAssistantView

VERSION = '1.1.0'

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def get_scanner(hass, config):
    """Set up an endpoint for the pfSense application
    and return PfsenseDeviceScanner."""
    scanner = PfsenseDeviceScanner()
    hass.http.register_view(PfsenseView(scanner))
    return scanner


class PfsenseDeviceScanner(DeviceScanner):
    """This class parses output from 'arp -a' on pfSense."""

    def __init__(self):
        """Initialize the scanner."""
        self.last_clients = {}

    def set_results(self, clients: dict):
        self.last_clients = clients

    def scan_devices(self) -> List[str]:
        """Return a list with found device MACs."""
        return list(self.last_clients)

    def get_device_name(self, device: str) -> str:
        """Return the provided device's name."""
        host = self.last_clients.get(device, {})
        return host.get("host_name")

    def get_extra_attributes(self, device: str) -> dict:
        """
        Get extra attributes of a device.

        Some known extra attributes that may be returned in the device tuple
        include MAC address (mac), network device (dev), IP address
        (ip), reachable status (reachable), associated router
        (host), hostname if known (hostname) among others.
        """
        return self.last_clients.get(device, {})


class PfsenseView(HomeAssistantView):
    """View to handle pfSense requests."""

    url = '/api/pfsense'
    name = 'api:pfsense'
    requires_auth = False

    def __init__(self, scanner):
        """Initialize pfSense URL endpoints."""
        self.scanner = scanner

    @asyncio.coroutine
    def post(self, request):
        """Received message from pfSense."""
        data = yield from request.post()
        file_contents = data['data'].file.read().decode("utf-8")

        _LOGGER.debug(file_contents)

        self.scanner.set_results(self._parse_post_data(file_contents))

    @staticmethod
    def _parse_post_data(file_contents):
        # Body comes back as one string
        clients = {}
        for entry in file_contents.split("\n"):
            split_entry = entry.split()

            # Non-interface entries have 11 fields
            if len(split_entry) != 11:
                continue

            hostname = split_entry[0]
            ip = split_entry[1].strip('()')
            mac = split_entry[3].upper()

            _LOGGER.debug(
                "Parsed ARP record: %s (%s) at %s", hostname, ip, mac)

            clients[mac] = {
                # ? is an unknown hostname to pfSense
                'host_name':
                    hostname if hostname != '?' else mac.replace(":", ""),
                'ip_address': ip,
            }
        return clients
