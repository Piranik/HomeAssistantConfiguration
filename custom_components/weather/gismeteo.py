"""
Support for GisMeteo.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/weather.gismeteo/
"""
from datetime import datetime, timedelta
import logging

import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_SPEED,
    ATTR_FORECAST_WIND_BEARING,
    PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (
    CONF_API_KEY, TEMP_CELSIUS, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME,
    STATE_UNKNOWN)
from homeassistant.helpers import config_validation as cv
from homeassistant.util import Throttle

REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Data provided by GisMeteo'

DEFAULT_NAME = 'GisMeteo'

# API limit is 50 req/day
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=40)

CONDITION_CLASSES = {
    "cloudy": [""],
    "clear-night": [""],
    "cloudy": [""],
    "fog": [""],
    "lightning": [""],
    "lightning-rainy": [""],
    "partlycloudy": [""],
    "pouring": [""],
    "rainy": [""],
    "snowy": [""],
    "snowy-rainy": [""],
    "sunny": [""],
    "windy": [""],
    "windy-variant": [""],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the GisMeteo weather platform."""
    from .lib import gismeteo

    longitude = config.get(CONF_LONGITUDE, round(hass.config.longitude, 6))
    latitude = config.get(CONF_LATITUDE, round(hass.config.latitude, 6))
    if None in (latitude, longitude):
        _LOGGER.error("No Latitude or Longitude set in Home Assistant config")
        return

    gm = gismeteo.Gismeteo()

    city = list(gm.cities_nearby(latitude, longitude, 1))[0]
    name = config.get(CONF_NAME)
    if name is None:
        name = city.get("name")

    add_entities([GisMeteoWeather(
        name, gm, city.get("id"), hass.config.units.temperature_unit)], True)


class GisMeteoWeather(WeatherEntity):
    """Implementation of an GisMeteo sensor."""

    def __init__(self, name, gm, city_id, temperature_unit):
        """Initialize the sensor."""
        self._name = name
        self._gm = gm
        self._city_id = city_id
        self._temperature_unit = temperature_unit
        self.data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def condition(self):
        """Return the current condition."""
        try:
            return [k for k, v in CONDITION_CLASSES.items() if
                    self.data.fact.condition in v][0]
        except IndexError:
            return STATE_UNKNOWN

    @property
    def temperature(self):
        """Return the current temperature."""
        return self.data.fact.temp

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the current pressure."""
        return self.data.fact.pressure

    @property
    def humidity(self):
        """Return the name of the sensor."""
        return self.data.fact.humidity

    @property
    def wind_speed(self):
        """Return the current windspeed."""
        return self.data.fact.wind_speed

    @property
    def wind_bearing(self):
        """Return the current wind bearing (degrees)."""
        return self.data.fact.wind_dir

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def forecast(self):
        """Return the forecast array."""
        data = []
        for entry in self.data.forecast:
            date = datetime.strptime(entry.date, "%Y-%m-%d")
            for part_name, part_dt in DAYPARTS_TIMEDELTA:
                part = entry.parts.get(part_name)
                if part is None:
                    continue
                data.append({
                    ATTR_FORECAST_TIME:
                        date + part_dt,
                    ATTR_FORECAST_TEMP:
                        part.temp_max,
                    ATTR_FORECAST_TEMP_LOW:
                        part.temp_min,
                    ATTR_FORECAST_PRECIPITATION:
                        part.prec_prob,
                    ATTR_FORECAST_WIND_SPEED:
                        part.wind_speed,
                    ATTR_FORECAST_WIND_BEARING:
                        WIND_DIR[part.wind_dir],
                    ATTR_FORECAST_CONDITION:
                        [k for k, v in CONDITION_CLASSES.items()
                         if part.condition in v][0],
                })
        return data

    def update(self):
        """Get the latest data from OWM and updates the states."""
        self.data = self._gm.forecast(self._city_id)
        _LOGGER.error(self.data)
