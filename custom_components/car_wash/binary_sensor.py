#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/HomeAssistantComponents/
"""
import logging
from datetime import datetime

import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.weather import (
    PLATFORM_SCHEMA, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TIME, ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW)
from homeassistant.const import (
    CONF_NAME, EVENT_HOMEASSISTANT_START, CONF_ICON)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change

REQUIREMENTS = []

VERSION = '0.0.2'

DEFAULT_NAME = 'Car Wash'
DEFAULT_ICON = 'mdi:car-wash'
DEFAULT_THRESHOLD = 70

PREDICTION_DAYS = 3

_LOGGER = logging.getLogger(__name__)

CONF_WEATHER = 'weather'
CONF_THRESHOLD = 'threshold'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_WEATHER): cv.entity_id,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.icon,
    vol.Optional(CONF_THRESHOLD, default=DEFAULT_THRESHOLD): vol.Coerce(int),
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Car Wash sensor."""
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('if you have ANY issues with this, please report them here:'
                 ' https://github.com/Limych/HomeAssistantComponents')

    name = config.get(CONF_NAME)
    weather = config.get(CONF_WEATHER)
    icon = config.get(CONF_ICON)
    threshold = config.get(CONF_THRESHOLD)

    async_add_entities([CarWashBinarySensor(hass, name, weather, icon, threshold)])


class CarWashBinarySensor(BinarySensorDevice):
    """Implementation of an Car Wash binary sensor."""

    def __init__(self, hass, friendly_name, weather_entity, icon, threshold):
        """Initialize the sensor."""
        self._hass = hass
        self._name = friendly_name
        self._weather_entity = weather_entity
        self._icon = icon
        self._threshold = threshold
        self._state = None

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            self.async_schedule_update_ha_state(True)

        @callback
        def sensor_startup(event):
            """Update template on startup."""
            async_track_state_change(self._hass, [self._weather_entity], sensor_state_listener)

            self.async_schedule_update_ha_state(True)

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return True is sensor is on."""
        if self._state is None:
            return None

        return self._state >= self._threshold

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    async def async_update(self):
        """Update the state from the template."""
        wd = self._hass.states.get(self._weather_entity).attributes
        t = wd.get('temperature')
        forecast = wd.get('forecast')

        if forecast is None:
            _LOGGER.error('Can\'t get forecast data from weather provider!')
            return

        stop_date = datetime.fromtimestamp(datetime.now().timestamp() + 86400 * PREDICTION_DAYS).strftime('%F')
        _LOGGER.debug('Inspect weather forecast from now till %s', stop_date)

        prediction = []
        for fc in forecast:
            if fc.get(ATTR_FORECAST_TIME)[:10] == stop_date:
                break

            wash = True
            if t <= 0 and fc.get(ATTR_FORECAST_TEMP_LOW) is not None:
                t = fc.get(ATTR_FORECAST_TEMP_LOW)
                wash &= t < 0
            if t <= 0 and fc.get(ATTR_FORECAST_TEMP) is not None:
                t = fc.get(ATTR_FORECAST_TEMP)
                wash &= t < 0
            wash &= not bool(fc.get(ATTR_FORECAST_PRECIPITATION, False))

            prediction.append(int(wash))

        _LOGGER.debug('Car wash forecast vector: %s', ''.join(str(x) for x in prediction))

        wash = 1
        for i in range(0, len(prediction)):
            if not prediction[i]:
                wash *= 0.95 - 0.9 * i / (len(prediction) - 1)

        self._state = int(round(wash * 100, 0))
        _LOGGER.debug('Car wash forecast %s%% while threshold is %s%%', self._state, self._threshold)
