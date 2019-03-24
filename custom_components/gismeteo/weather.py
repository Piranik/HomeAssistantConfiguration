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
import re

import voluptuous as vol
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED, PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (
    TEMP_CELSIUS, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, STATE_UNKNOWN)
from homeassistant.helpers import config_validation as cv, sun
from homeassistant.util import dt as dt_util, Throttle

from .const import (
    ATTR_FORECAST_HUMIDITY, ATTR_FORECAST_PRESSURE, ATTRIBUTION,
    DEFAULT_NAME, MIN_TIME_BETWEEN_UPDATES, CONDITION_FOG_CLASSES)

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
    latitude = config.get(CONF_LATITUDE, round(hass.config.latitude, 6))
    longitude = config.get(CONF_LONGITUDE, round(hass.config.longitude, 6))
    name = config.get(CONF_NAME)

    _LOGGER.debug("Initializing for coordinates %s, %s", latitude, longitude)

    from . import _gismeteo
    gm = _gismeteo.Gismeteo()

    city = list(gm.cities_nearby(latitude, longitude, 1))[0]
    _LOGGER.debug("Nearby detected city is %s", city.get("name"))

    wd = WeatherData(gm, city.get("id"))

    add_entities([GismeteoWeather(hass, name, wd)], True)


class GismeteoWeather(WeatherEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, hass, station_name, wd):
        """Initialize the sensor."""
        self._hass = hass
        self._station_name = station_name
        self._wd = wd
        self.data = None

    def update(self):
        """Get the latest data from Gismeteo and updates the states."""
        data = self._wd.get_data()

        if data is not None:        
            data['days'] = list(data['days'])
            for day in data['days']:
                if day.get('hourly') is not None:
                    day['hourly'] = list(day['hourly'])
            self.data = data
            _LOGGER.debug("Weather data updated: %s", str(data))

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
        return self._get_condition()

    @property
    def temperature(self):
        """Return the current temperature."""
        return self._get_temperature()

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the current pressure."""
        return self._get_pressure_hpa()

    @property
    def humidity(self):
        """Return the name of the sensor."""
        return self._get_humidity()

    @property
    def wind_bearing(self):
        """Return the current wind bearing."""
        return self._get_wind_bearing()

    @property
    def wind_speed(self):
        """Return the current windspeed."""
        return self._get_wind_speed_kmh()

    @property
    def forecast(self):
        """Return the forecast array."""
        data = []
        for entry in self.data['days']:
            if entry.get('hourly') is None:
                data.append({
                    ATTR_FORECAST_TIME:
                        entry['date']['local'],
                    ATTR_FORECAST_CONDITION:
                        self._get_condition(entry),
                    ATTR_FORECAST_TEMP:
                        entry['temperature']['max'],
                    ATTR_FORECAST_TEMP_LOW:
                        entry['temperature']['min'],
                    ATTR_FORECAST_PRESSURE:
                        self._get_pressure_hpa(entry),
                    ATTR_FORECAST_HUMIDITY:
                        self._get_humidity(entry),
                    ATTR_FORECAST_WIND_SPEED:
                        self._get_wind_speed_kmh(entry),
                    ATTR_FORECAST_WIND_BEARING:
                        self._get_wind_bearing(entry),
                    ATTR_FORECAST_PRECIPITATION:
                        int(entry['precipitation']['type'] != 0),
                })
            else:
                for part in entry['hourly']:
                    if dt_util.utcnow() < dt_util.utc_from_timestamp(part['date']['unix']):
                        data.append({
                            ATTR_FORECAST_TIME:
                                part['date']['local'],
                            ATTR_FORECAST_CONDITION:
                                self._get_condition(part),
                            ATTR_FORECAST_TEMP:
                                self._get_temperature(part),
                            ATTR_FORECAST_PRESSURE:
                                self._get_pressure_hpa(part),
                            ATTR_FORECAST_HUMIDITY:
                                self._get_humidity(part),
                            ATTR_FORECAST_WIND_SPEED:
                                self._get_wind_speed_kmh(part),
                            ATTR_FORECAST_WIND_BEARING:
                                self._get_wind_bearing(part),
                            ATTR_FORECAST_PRECIPITATION:
                                int(part['precipitation']['type'] != 0),
                        })
        return data

    def _get_condition(self, src=None):
        """Return the current condition."""
        src = src or self.data['current']
        cond = STATE_UNKNOWN
        try:
            if src['cloudiness'] == 0:
                if sun.is_up(self._hass, dt_util.utc_from_timestamp(src['date']['unix'])):
                    cond = "sunny"          # Sunshine
                else:
                    cond = "clear-night"    # Clear night
            elif src['cloudiness'] == 1:
                cond = "partlycloudy"       # A few clouds
            elif src['cloudiness'] == 2:
                cond = "cloudy"             # Many clouds
            elif src['cloudiness'] == 3:
                cond = "cloudy"             # Many clouds

            pr_type = src['precipitation']['type']
            pr_int = src['precipitation']['intensity']
            if src['storm']:
                cond = "lightning"          # Lightning/ thunderstorms
                if pr_type != 0:
                    cond = "lightning-rainy"    # Lightning/ thunderstorms and rain
            elif pr_type == 1:
                cond = "rainy"              # Rain
                if pr_int == 3:
                    cond = "pouring"        # Pouring rain
            elif pr_type == 2:
                cond = "snowy"              # Snow
            elif pr_type == 3:
                cond = "snowy-rainy"        # Snow and Rain
            elif self._get_wind_speed_ms(src) > 10.8:
                if cond == "cloudy":
                    cond = "windy-variant"  # Wind and clouds
                else:
                    cond = "windy"          # Wind
            elif src['cloudiness'] == 0 and src.get('phenomenon') is not None \
                    and src['phenomenon'] in CONDITION_FOG_CLASSES:
                cond = "fog"                # Fog
        except:
            # _LOGGER.error(sys.exc_info())
            raise
        return cond

    def _get_temperature(self, src=None):
        """Return the current temperature."""
        src = src or self.data['current']
        return int(src['temperature']['air'])

    def _get_pressure_hpa(self, src=None):
        """Return the current pressure in hPa."""
        return round(self._get_pressure_mmhg(src) * 1.33322, 1)

    def _get_pressure_mmhg(self, src=None):
        """Return the current pressure in mmHg."""
        src = src or self.data['current']
        res = src['pressure']
        if isinstance(res, dict):
            res = res['avg']
        return float(res)

    def _get_humidity(self, src=None):
        """Return the name of the sensor."""
        src = src or self.data['current']
        res = src['humidity']
        if isinstance(res, dict):
            res = res['avg']
        return int(res)

    def _get_wind_bearing(self, src=None):
        """Return the current wind bearing."""
        src = src or self.data['current']
        w_dir = int(src['wind']['direction'])
        if w_dir > 0:
            return (w_dir - 1) * 45
        else:
            return STATE_UNKNOWN

    def _get_wind_speed_kmh(self, src=None):
        """Return the current windspeed in km/h."""
        return round(self._get_wind_speed_ms(src) * 3.6, 1)

    def _get_wind_speed_ms(self, src=None):
        """Return the current windspeed in m/s."""
        src = src or self.data['current']
        res = src['wind']['speed']
        if isinstance(res, dict):
            res = res['avg']
        return float(res)


class WeatherData:
    """Get the latest data from Gismeteo."""

    def __init__(self, gm, city_id):
        """Initialize the data object."""
        self.gm = gm
        self.city_id = city_id

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def get_data(self):
        """Get the latest data from Gismeteo."""
        _LOGGER.debug("Fetching data from Gismeteo for city_id %s", str(self.city_id))
        data = self.gm.forecast(self.city_id)
        if data is None:
            _LOGGER.warning("Failed to fetch data from Gismeteo")
            return None

        return data
