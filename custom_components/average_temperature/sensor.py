#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Average Temperature Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/HomeAssistantComponents/
"""
import logging
import math
import re

import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components import history
from homeassistant.const import (
    CONF_NAME, CONF_ENTITIES, EVENT_HOMEASSISTANT_START, ATTR_UNIT_OF_MEASUREMENT, TEMP_CELSIUS, TEMP_FAHRENHEIT,
    UNIT_NOT_RECOGNIZED_TEMPLATE, TEMPERATURE, ATTR_TEMPERATURE)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.util.temperature import convert as convert_temperature

VERSION = '1.1.1'

_LOGGER = logging.getLogger(__name__)

CONF_DURATION = 'duration'

DEFAULT_NAME = 'Average Temperature'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITIES): cv.entity_ids,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_DURATION): cv.time_period,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Gismeteo weather platform."""
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('if you have ANY issues with this, please report them here:'
                 ' https://github.com/Limych/HomeAssistantComponents')

    name = config.get(CONF_NAME)
    duration = config.get(CONF_DURATION)
    entities = config.get(CONF_ENTITIES)

    async_add_entities([AverageTemperatureSensor(hass, name, duration, entities)])


class AverageTemperatureSensor(Entity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, hass, friendly_name, measure_duration, entities):
        """Initialize the sensor."""
        self._hass = hass
        self._name = friendly_name
        self._duration = measure_duration
        self._entities = entities
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
            async_track_state_change(self._hass, self._entities, sensor_state_listener)

            self.async_schedule_update_ha_state(True)

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._hass.config.units.temperature_unit

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return 'mdi:thermometer'

    def _convert_temp(self, temperature, temperature_unit: str) -> float:
        """Convert temperature to Home Assistant common configured units."""
        if temperature is not None:
            ha_unit = self._hass.config.units.temperature_unit
            temperature = float(temperature)

            if temperature_unit != ha_unit:
                temperature = convert_temperature(temperature, temperature_unit, ha_unit)

        return temperature

    async def async_update(self):
        """Update the sensor state."""
        start = now = start_timestamp = now_timestamp = unit = None
        if self._duration is not None:
            now = dt_util.now()
            start = dt_util.as_utc(now - self._duration)
            now = dt_util.as_utc(now)

            # Compute integer timestamps
            start_timestamp = math.floor(dt_util.as_timestamp(start))
            now_timestamp = math.floor(dt_util.as_timestamp(now))

        values = []

        for entity_id in self._entities:
            _LOGGER.debug('Processing entity \'%s\'', entity_id)

            entity = self._hass.states.get(entity_id)

            if entity is None:
                raise HomeAssistantError(
                    'Unable to find an entity called {}'.format(entity_id))

            as_attribute = re.match(r'weather\.', entity_id)
            if not as_attribute:
                unit = entity.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
                if unit not in (TEMP_CELSIUS, TEMP_FAHRENHEIT):
                    raise ValueError(UNIT_NOT_RECOGNIZED_TEMPLATE.format(unit, TEMPERATURE))

            value = 0
            elapsed = 0

            if self._duration is None:
                # Get current state
                if as_attribute:
                    value = entity.attributes.get(ATTR_TEMPERATURE)
                else:
                    value = self._convert_temp(entity.state, unit)
                _LOGGER.debug('Current temperature: %s', value)

            else:
                # Get history between start and now
                history_list = history.state_changes_during_period(
                    self.hass, start, now, str(entity_id))

                if entity_id not in history_list.keys():
                    continue

                # Get the first state
                item = history.get_state(self.hass, start, entity_id)
                _LOGGER.debug('Initial historical state: %s', item)
                last_state = None
                last_time = start_timestamp
                if item is not None and item.state is not None:
                    if as_attribute:
                        last_state = item.attributes.get(ATTR_TEMPERATURE)
                    else:
                        last_state = self._convert_temp(item.state, unit)

                # Get the other states
                for item in history_list.get(entity_id):
                    _LOGGER.debug('Historical state: %s', item)
                    if item.state is not None:
                        if as_attribute:
                            current_state = item.attributes.get(ATTR_TEMPERATURE)
                        else:
                            current_state = self._convert_temp(item.state, unit)
                        current_time = item.last_changed.timestamp()

                        if last_state:
                            last_elapsed = current_time - last_time
                            value += last_state * last_elapsed
                            elapsed += last_elapsed

                        last_state = current_state
                        last_time = current_time

                # Count time elapsed between last history state and now
                if last_state:
                    last_elapsed = now_timestamp - last_time
                    value += last_state * last_elapsed
                    elapsed += last_elapsed

                value /= elapsed
                _LOGGER.debug('Historical average temperature: %s', value)

            values.append(value)

        if values:
            self._state = round(sum(values) / len(values), 1)
        else:
            self._state = None
        _LOGGER.debug('Total average temperature: %s', self._state)
