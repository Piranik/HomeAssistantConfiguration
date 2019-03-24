#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
"""
Support for Gismeteo.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/weather.gismeteo/
"""
import logging
import os

import voluptuous as vol
from homeassistant.components.weather import (
    PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (
    TEMP_CELSIUS, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME)
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME, MIN_TIME_BETWEEN_UPDATES, CONF_CACHE_DIR, DEFAULT_CACHE_DIR)

REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
})


def setup_platform(hass, config, add_entities,
                   discovery_info=None):
    """Set up the Gismeteo weather platform."""
    name = config.get(CONF_NAME)
    latitude = config.get(CONF_LATITUDE, round(hass.config.latitude, 6))
    longitude = config.get(CONF_LONGITUDE, round(hass.config.longitude, 6))
    cache_dir = config.get(CONF_CACHE_DIR, DEFAULT_CACHE_DIR)

    _LOGGER.debug("Initializing for coordinates %s, %s", latitude, longitude)

    from . import _gismeteo
    gm = _gismeteo.Gismeteo(params={
        'cache_dir': str(cache_dir) + '/gismeteo' if os.access(cache_dir, os.X_OK | os.W_OK) else None,
        'cache_time': MIN_TIME_BETWEEN_UPDATES.total_seconds(),
    })

    city = list(gm.cities_nearby(latitude, longitude, 1))[0]
    _LOGGER.debug("Nearby detected city is %s", city.get("name"))

    wd = _gismeteo.WeatherData(hass, gm, city.get("id"))

    add_entities([GismeteoWeather(name, wd)], True)


class GismeteoWeather(WeatherEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, station_name, weather_data):
        """Initialize the sensor."""
        self._station_name = station_name
        self._wd = weather_data

    def update(self):
        """Get the latest data from Gismeteo and updates the states."""
        self._wd.update()

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._station_name

    @property
    def condition(self):
        """Return the current condition."""
        return self._wd.condition()

    @property
    def temperature(self):
        """Return the current temperature."""
        return self._wd.temperature()

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the current pressure."""
        return self._wd.pressure_hpa()

    @property
    def humidity(self):
        """Return the name of the sensor."""
        return self._wd.humidity()

    @property
    def wind_bearing(self):
        """Return the current wind bearing."""
        return self._wd.wind_bearing()

    @property
    def wind_speed(self):
        """Return the current windspeed."""
        return self._wd.wind_speed_kmh()

    @property
    def forecast(self):
        """Return the forecast array."""
        return self._wd.forecast()
