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

import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING, ATTR_FORECAST_WIND_SPEED,
    PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_MONITORED_CONDITIONS, CONF_NAME, TEMP_CELSIUS)
from homeassistant.helpers import config_validation as cv
from homeassistant.util import Throttle

from .const import (
    ATTR_FORECAST_HUMIDITY, ATTR_FORECAST_PRESSURE, ATTRIBUTION,
    DEFAULT_NAME, MIN_TIME_BETWEEN_UPDATES, CONDITION_FOG_CLASSES)

REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

CONF_FORECAST = 'forecast'
CONF_LANGUAGE = 'language'

SENSOR_TYPES = {
    'weather': ['Condition', None],
    'temperature': ['Temperature', TEMP_CELSIUS],
    'wind_speed': ['Wind speed', 'm/s'],
    'wind_bearing': ['Wind bearing', '°'],
    'humidity': ['Humidity', '%'],
    'pressure': ['Pressure', 'mbar'],
    'clouds': ['Cloud coverage', '%'],
    'rain': ['Rain', 'mm'],
    'snow': ['Snow', 'mm'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_FORECAST, default=False): cv.boolean,
    vol.Optional(CONF_LANGUAGE, default='en'): cv.string,
})


def setup_platform(hass, config, add_entities,
                   discovery_info=None):
    """Set up the Gismeteo weather platform."""

    if None in (hass.config.latitude, hass.config.longitude):
        _LOGGER.error("Latitude or longitude not set in Home Assistant config")
        return
    latitude = round(hass.config.latitude, 6)
    longitude = round(hass.config.longitude, 6)

    name = config.get(CONF_NAME)
    forecast = config.get(CONF_FORECAST)
    language = config.get(CONF_LANGUAGE).lower()[:2]

    _LOGGER.debug("Initializing for coordinates %s, %s", latitude, longitude)

    from . import _gismeteo
    gm = _gismeteo.Gismeteo(params={'lang': language})

    city = list(gm.cities_nearby(latitude, longitude, 1))[0]
    _LOGGER.debug("Nearby detected city is %s", city.get("name"))

    wd = WeatherData(gm, city.get("id"))

    dev = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        dev.append(GismeteoSensor(
            name, wd, variable, SENSOR_TYPES[variable][1]))

    if forecast:
        SENSOR_TYPES['forecast'] = ['Forecast', None]
        dev.append(GismeteoSensor(
            name, wd, 'forecast', SENSOR_TYPES['temperature'][1]))

    add_entities(dev, True)


class GismeteoSensor(Entity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, station_name, weather_data, sensor_type, temp_unit):
        """Initialize the sensor."""
        self.client_name = station_name
        self._name = SENSOR_TYPES[sensor_type][0]
        self._wd = weather_data
        self.temp_unit = temp_unit
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]

    def update(self):
        """Get the latest data from Gismeteo and updates the states."""
        self._wd.update()
        data = self._wd.data
        if data is None:
            return
        
        try:
            if self.type == 'weather':
                self._state = data['current']['description']
        except KeyError:
            self._state = None
            _LOGGER.warning("Condition is currently not available: %s", self.type)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self._name)

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    # @property
    # def forecast(self):
    #     """Return the forecast array."""
    #     data = []
    #     for entry in self.data['days']:
    #         if entry.get('hourly') is not None:
    #             for part in entry['hourly']:
    #                 data.append({
    #                     ATTR_FORECAST_TIME:
    #                         part['date']['local'],
    #                     ATTR_FORECAST_CONDITION:
    #                         self._get_condition(part),
    #                     ATTR_FORECAST_TEMP:
    #                         self._get_temperature(part),
    #                     ATTR_FORECAST_PRESSURE:
    #                         self._get_pressure_hpa(part),
    #                     ATTR_FORECAST_HUMIDITY:
    #                         self._get_humidity(part),
    #                     ATTR_FORECAST_WIND_SPEED:
    #                         self._get_wind_speed_kmh(part),
    #                     ATTR_FORECAST_WIND_BEARING:
    #                         self._get_wind_bearing(part),
    #                     ATTR_FORECAST_PRECIPITATION:
    #                         int(part['precipitation']['type'] != 0),
    #                 })
    #     return data

    # def _get_temperature(self, src=None):
    #     """Return the current temperature."""
    #     src = src or self.data['current']
    #     return int(src['temperature']['air'])

    # def _get_pressure_hpa(self, src=None):
    #     """Return the current pressure in hPa."""
    #     return round(self._get_pressure_mmhg(src) * 1.33322, 1)

    # def _get_pressure_mmhg(self, src=None):
    #     """Return the current pressure in mmHg."""
    #     src = src or self.data['current']
    #     return float(src['pressure'])

    # def _get_humidity(self, src=None):
    #     """Return the name of the sensor."""
    #     src = src or self.data['current']
    #     return int(src['humidity'])

    # def _get_wind_bearing(self, src=None):
    #     """Return the current wind bearing."""
    #     src = src or self.data['current']
    #     w_dir = int(src['wind']['direction'])
    #     if w_dir > 0:
    #         return (w_dir - 1) * 45
    #     else:
    #         return STATE_UNKNOWN

    # def _get_wind_speed_kmh(self, src=None):
    #     """Return the current windspeed in km/h."""
    #     return round(self._get_wind_speed_ms(src) * 3.6, 1)

    # def _get_wind_speed_ms(self, src=None):
    #     """Return the current windspeed in m/s."""
    #     src = src or self.data['current']
    #     return float(src['wind']['speed'])


class WeatherData:
    """Get the latest data from Gismeteo."""

    def __init__(self, gm, city_id):
        """Initialize the data object."""
        self.gm = gm
        self.city_id = city_id
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Gismeteo."""
        _LOGGER.debug("Fetching data from Gismeteo for city_id %s", str(self.city_id))
        self.data = self.gm.forecast(self.city_id)
        if self.data is None:
            _LOGGER.warning("Failed to fetch data from Gismeteo")
            return
        
        self.data['days'] = list(self.data['days'])
        for day in self.data['days']:
            if day.get('hourly') is not None:
                day['hourly'] = list(day['hourly'])
            
        _LOGGER.debug("New weather data: %s", str(self.data))
