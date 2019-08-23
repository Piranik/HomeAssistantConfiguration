"""
Component to integrate with Radon.ru.

For more details about this component, please refer to
https://github.com/Limych/ha-radon
"""

import logging
import os

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

# Base component constants
DOMAIN = "radon"
VERSION = "0.1.0"
ISSUE_URL = "https://github.com/Limych/ha-radon/issues"
REQUIRED_FILES = [
    # "cache.py",
    # "const.py",
    # "manifest.json",
    # "sensor.py",
]

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_LATITUDE): cv.latitude,
            vol.Optional(CONF_LONGITUDE): cv.longitude,
        })
    ]),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Radon component."""
    _LOGGER.fatal('TEST')
    # Print startup message
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('If you have any issues with this you need to open an issue '
                 'here: %s', ISSUE_URL)

    # Check that all required files are present
    if not _check_files(hass):
        return False

    for index, sensor_config in enumerate(config.get(DOMAIN, [
        {
            CONF_NAME: '%s Radiation Level' % hass.config.location_name,
        },
    ])):
        latitude = sensor_config.get(CONF_LATITUDE)
        longitude = sensor_config.get(CONF_LONGITUDE)

        if latitude is None and longitude is None:
            latitude = round(hass.config.longitude, 6)
            longitude = round(hass.config.longitude, 6)

        name = sensor_config.get(CONF_NAME,
                                 "Radiation Level #%d" % (index + 1))

        if latitude is None or longitude is None:
            _LOGGER.error('Incorrect latitude/longitude configuration '
                          'for sensor "%s"! '
                          'Please check configs.', name)
            continue

        # discovery.load_platform(hass, SENSOR, DOMAIN, {
        #     CONF_NAME: name,
        #     CONF_LATITUDE: latitude,
        #     CONF_LONGITUDE: longitude,
        # }, config)
        _LOGGER.debug('Added sensor "%s"' % name)

    return True


def _check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all required files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        return False

    return True
