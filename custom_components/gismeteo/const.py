#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
"""
Support for Gismeteo.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/weather.gismeteo/
"""

from datetime import timedelta

VERSION = '1.0'

ATTRIBUTION = 'Data provided by Gismeteo'

CONF_CACHE_DIR = 'cache_dir'

DEFAULT_NAME = 'Gismeteo'
DEFAULT_CACHE_DIR = '/tmp'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

CONDITION_FOG_CLASSES = [11, 12, 28, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                         49, 120, 130, 131, 132, 133, 134, 135, 528]

ATTR_FORECAST_HUMIDITY = 'humidity'
ATTR_FORECAST_PRESSURE = 'pressure'
