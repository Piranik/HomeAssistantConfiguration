#
#  Copyright (c) 2018, Vladimir Maksimenko <vl.maksime@gmail.com>
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

import calendar
import os
import time
import xml.etree.cElementTree as etree

from future.utils import (PY3, iteritems)
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED)
from homeassistant.const import (
    STATE_UNKNOWN)
from homeassistant.helpers import sun
from homeassistant.util import dt as dt_util, Throttle

from .const import (
    ATTR_FORECAST_HUMIDITY, ATTR_FORECAST_PRESSURE, MIN_TIME_BETWEEN_UPDATES,
    CONDITION_FOG_CLASSES)

if PY3:
    from urllib.request import (urlopen, quote)
    from io import open
else:
    from urllib import (urlopen, quote)

try:
    etree.fromstring('<?xml version="1.0"?><foo><bar/></foo>')
except TypeError:
    import xml.etree.ElementTree as etree

REQUIREMENTS = []


class Cache(object):
    def __init__(self, params=None):
        params = params or {}

        self._cache_dir = params.get('cache_dir', '')
        self._cache_time = params.get('cache_time', 0)

        self._clear_dir()

    def _clear_dir(self):
        now_time = time.time()

        if self._cache_dir != '' \
                and os.path.exists(self._cache_dir):
            files = os.listdir(self._cache_dir)
            for file_name in files:
                file_path = self._get_file_path(file_name)
                file_time = os.path.getmtime(file_path)

                if (file_time + self._cache_time) <= now_time:
                    os.remove(file_path)

    def _get_file_path(self, file_name):
        return os.path.join(self._cache_dir, file_name)

    def is_cached(self, file_name):
        result = False

        file_path = self._get_file_path(file_name)
        if os.path.exists(file_path) \
                and os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            now_time = time.time()

            result = (file_time + self._cache_time) >= now_time

        return result

    def read_cache(self, file_name):
        file_path = self._get_file_path(file_name)
        if os.path.exists(file_path) \
                and os.path.isfile(file_path):
            file = open(file_path)
            content = file.read()
            file.close()
        else:
            content = None

        return content

    def save_cache(self, file_name, content):
        if self._cache_dir:
            if not os.path.exists(self._cache_dir):
                os.makedirs(self._cache_dir)

            file_path = self._get_file_path(file_name)

            file = open(file_path, "w")
            if PY3:
                file.write(content.decode('utf-8'))
            else:
                file.write(content)
            file.close()


class Gismeteo(object):

    def __init__(self, params=None):
        params = params or {}
        base_url = 'https://services.gismeteo.ru/inform-service/inf_chrome'

        self._lang = params.get('lang', 'en')
        self._cache = Cache(params) if params.get('cache_dir') is not None else None
        self._actions = {'cities_search': base_url + '/cities/?startsWith=#keyword&lang=#lang',
                         'cities_ip': base_url + '/cities/?mode=ip&count=1&nocache=1&lang=#lang',
                         'cities_nearby': base_url + '/cities/?lat=#lat&lng=#lng&count=#count&nocache=1&lang=#lang',
                         'forecast': base_url + '/forecast/?city=#city_id&lang=#lang',
                         }

    def _http_request(self, action, url_params=None):
        url_params = url_params or {}

        if self._use_cache(action):
            file_name = self._get_file_name(action, url_params)
            if self._cache.is_cached(file_name):
                return self._cache.read_cache(file_name)

        url = self._actions.get(action)

        for key, val in iteritems(url_params):
            url = url.replace(key, str(val))

        try:
            req = urlopen(url)
        except IOError:
            return ''

        response = req.read()
        req.close()

        if self._use_cache(action) and response:
            self._cache.save_cache(file_name, response)

        return response

    @staticmethod
    def _get_locations_list(xml):
        root = etree.fromstring(xml)
        if root is not None:
            for item in root:
                location = {'name': item.attrib['n'],
                            'id': item.attrib['id'],
                            'country': item.attrib['country_name'],
                            'district': item.attrib.get('district_name', ''),
                            'lat': item.attrib['lat'],
                            'lng': item.attrib['lng'],
                            'kind': item.attrib['kind'],
                            }

                yield location

    @staticmethod
    def _get_date(source, tzone):
        if isinstance(source, float):
            local_stamp = source
            local_date = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(local_stamp))
        else:
            local_date = source if len(source) > 10 else source + 'T00:00:00'
            local_stamp = 0

            while local_stamp == 0:
                local_stamp = calendar.timegm(time.strptime(local_date, '%Y-%m-%dT%H:%M:%S'))

        utc_stamp = local_stamp - tzone * 60
        result = {'local': local_date,
                  'utc': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(utc_stamp)),
                  'unix': utc_stamp,
                  'offset': tzone}
        return result

    @staticmethod
    def _get_file_name(action, url_params):
        file_name = action
        for key, val in iteritems(url_params):
            file_name = '{0}_{1}'.format(file_name, val)

        return file_name + '.xml'

    def _use_cache(self, action):
        cached_actions = ['forecast', 'cities_ip']

        return self._cache is not None \
               and action in cached_actions

    def _get_forecast_info(self, xml):
        root = etree.fromstring(xml)
        if root is not None:
            xml_location = root[0]

            return {'name': xml_location.attrib['name'],
                    'id': xml_location.attrib['id'],
                    'kind': xml_location.attrib['kind'],
                    'country': xml_location.attrib['country_name'],
                    'district': xml_location.attrib.get('district_name', ''),
                    'lat': xml_location.attrib['lat'],
                    'lng': xml_location.attrib['lng'],
                    'cur_time': self._get_date(xml_location.attrib['cur_time'], int(xml_location.attrib['tzone'])),
                    'current': self._get_fact_forecast(xml_location),
                    'days': self._get_days_forecast(xml_location),
                    }

    def _get_item_forecast(self, xml_item, tzone):
        result = {}
        xml_values = xml_item[0]

        result['date'] = self._get_date(xml_item.attrib['valid'], tzone)
        if xml_item.attrib.get('sunrise') is not None:
            result['sunrise'] = self._get_date(float(xml_item.attrib['sunrise']), tzone)
        if xml_item.attrib.get('sunset') is not None:
            result['sunset'] = self._get_date(float(xml_item.attrib['sunset']), tzone)
        result['temperature'] = {'air': int(xml_values.attrib['t']),
                                 'comfort': int(xml_values.attrib['hi']),
                                 }
        if xml_values.attrib.get('tflt') is not None:
            result['temperature']['air'] = float(xml_values.attrib['tflt'])
        if xml_values.attrib.get('tcflt') is not None:
            result['temperature']['comfort'] = float(xml_values.attrib['tcflt'])
        if xml_values.attrib.get('water_t') is not None:
            result['temperature']['water'] = int(xml_values.attrib['water_t'])
        result['description'] = xml_values.attrib['descr']
        result['humidity'] = int(xml_values.attrib['hum'])
        result['pressure'] = int(xml_values.attrib['p'])
        result['cloudiness'] = int(xml_values.attrib['cl'])
        result['storm'] = (xml_values.attrib['ts'] == '1')
        result['precipitation'] = {'type': int(xml_values.attrib['pt']),
                                   'amount': xml_values.attrib.get('prflt'),
                                   'intensity': int(xml_values.attrib['pr']),
                                   }
        if xml_values.attrib.get('ph') is not None \
                and xml_values.attrib['ph']:
            result['phenomenon'] = int(xml_values.attrib['ph']),
        if xml_item.attrib.get('tod') is not None:
            result['tod'] = int(xml_item.attrib['tod'])
        result['icon'] = xml_values.attrib['icon']
        result['gm'] = int(xml_values.attrib['grade'])
        result['wind'] = {'speed': float(xml_values.attrib['ws']),
                          'direction': int(xml_values.attrib['wd']),
                          }

        return result

    def _get_fact_forecast(self, xml_location):
        fact = xml_location.find('fact')
        return self._get_item_forecast(fact, int(xml_location.attrib['tzone']))

    def _get_days_forecast(self, xml_location):
        tzone = int(xml_location.attrib['tzone'])
        for xml_day in xml_location.findall('day'):

            if xml_day.attrib.get('icon') is None:
                continue

            day = {'date': self._get_date(xml_day.attrib['date'], tzone),
                   'sunrise': self._get_date(float(xml_day.attrib['sunrise']), tzone),
                   'sunset': self._get_date(float(xml_day.attrib['sunset']), tzone),
                   'temperature': {'min': int(xml_day.attrib['tmin']),
                                   'max': int(xml_day.attrib['tmax']),
                                   },
                   'description': xml_day.attrib['descr'],
                   'humidity': {'min': int(xml_day.attrib['hummin']),
                                'max': int(xml_day.attrib['hummax']),
                                'avg': int(xml_day.attrib['hum']),
                                },
                   'pressure': {'min': int(xml_day.attrib['pmin']),
                                'max': int(xml_day.attrib['pmax']),
                                'avg': int(xml_day.attrib['p']),
                                },
                   'cloudiness': int(xml_day.attrib['cl']),
                   'storm': (xml_day.attrib['ts'] == '1'),
                   'precipitation': {'type': xml_day.attrib['pt'],
                                     'amount': xml_day.attrib['prflt'],
                                     'intensity': xml_day.attrib['pr'],
                                     },
                   'icon': xml_day.attrib['icon'],
                   'gm': int(xml_day.attrib['grademax']),
                   'wind': {'speed': {'min': round(float(xml_day.attrib['wsmin']), 1),
                                      'max': round(float(xml_day.attrib['wsmax']), 1),
                                      'avg': round(float(xml_day.attrib['ws']), 1),
                                      },
                            'direction': xml_day.attrib['wd'],
                            },
                   }
            if len(xml_day):
                day['hourly'] = self._get_hourly_forecast(xml_day, tzone)

            yield day

    def _get_hourly_forecast(self, xml_day, tzone):
        for xml_forecast in xml_day.findall('forecast'):
            yield self._get_item_forecast(xml_forecast, tzone)

    def cities_search(self, keyword):

        url_params = {'#keyword': quote(keyword),
                      '#lang': self._lang,
                      }

        response = self._http_request('cities_search', url_params)

        if response:
            return self._get_locations_list(response)
        else:
            return None

    def cities_ip(self):
        url_params = {'#lang': self._lang}

        response = self._http_request('cities_ip', url_params)
        if response:
            locations = self._get_locations_list(response)
            for location in locations:
                return location
        return None

    def cities_nearby(self, lat, lng, count=5):
        url_params = {'#lat': lat,
                      '#lng': lng,
                      '#count': count,
                      '#lang': self._lang,
                      }

        response = self._http_request('cities_nearby', url_params)
        if response:
            return self._get_locations_list(response)
        else:
            return None

    def forecast(self, city_id):
        url_params = {'#city_id': city_id,
                      '#lang': self._lang,
                      }

        response = self._http_request('forecast', url_params)
        if response:
            return self._get_forecast_info(response)
        else:
            return None


class WeatherData:
    """Get the latest data from Gismeteo."""

    def __init__(self, hass, gismeteo, city_id):
        """Initialize the data object."""
        self._hass = hass
        self.gm = gismeteo
        self.city_id = city_id
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Gismeteo."""
        self.data = self.gm.forecast(self.city_id)
        if self.data is None:
            return

        self.data['days'] = list(self.data['days'])
        for day in self.data['days']:
            if day.get('hourly') is not None:
                day['hourly'] = list(day['hourly'])

    def condition(self, src=None):
        """Return the current condition."""
        src = src or self.data['current']
        cond = STATE_UNKNOWN

        if src['cloudiness'] == 0:
            if sun.is_up(self._hass, dt_util.utc_from_timestamp(src['date']['unix'])):
                cond = "sunny"  # Sunshine
            else:
                cond = "clear-night"  # Clear night
        elif src['cloudiness'] == 1:
            cond = "partlycloudy"  # A few clouds
        elif src['cloudiness'] == 2:
            cond = "cloudy"  # Many clouds
        elif src['cloudiness'] == 3:
            cond = "cloudy"  # Many clouds

        pr_type = src['precipitation']['type']
        pr_int = src['precipitation']['intensity']
        if src['storm']:
            cond = "lightning"  # Lightning/ thunderstorms
            if pr_type != 0:
                cond = "lightning-rainy"  # Lightning/ thunderstorms and rain
        elif pr_type == 1:
            cond = "rainy"  # Rain
            if pr_int == 3:
                cond = "pouring"  # Pouring rain
        elif pr_type == 2:
            cond = "snowy"  # Snow
        elif pr_type == 3:
            cond = "snowy-rainy"  # Snow and Rain
        elif self.wind_speed_ms(src) > 10.8:
            if cond == "cloudy":
                cond = "windy-variant"  # Wind and clouds
            else:
                cond = "windy"  # Wind
        elif src['cloudiness'] == 0 and src.get('phenomenon') is not None \
                and src['phenomenon'] in CONDITION_FOG_CLASSES:
            cond = "fog"  # Fog

        return cond

    def temperature(self, src=None):
        """Return the current temperature."""
        src = src or self.data['current']
        src = src['temperature']
        if src.get('air') is not None:
            return src['air']
        else:
            return src['max']

    def pressure_hpa(self, src=None):
        """Return the current pressure in hPa."""
        return round(self.pressure_mmhg(src) * 1.33322, 1)

    def pressure_mmhg(self, src=None):
        """Return the current pressure in mmHg."""
        src = src or self.data['current']
        res = src['pressure']
        if isinstance(res, dict):
            res = res['avg']
        return float(res)

    def humidity(self, src=None):
        """Return the name of the sensor."""
        src = src or self.data['current']
        res = src['humidity']
        if isinstance(res, dict):
            res = res['avg']
        return int(res)

    def wind_bearing(self, src=None):
        """Return the current wind bearing."""
        src = src or self.data['current']
        w_dir = int(src['wind']['direction'])
        if w_dir > 0:
            return (w_dir - 1) * 45
        else:
            return STATE_UNKNOWN

    def wind_speed_kmh(self, src=None):
        """Return the current windspeed in km/h."""
        return round(self.wind_speed_ms(src) * 3.6, 1)

    def wind_speed_ms(self, src=None):
        """Return the current windspeed in m/s."""
        src = src or self.data['current']
        res = src['wind']['speed']
        if isinstance(res, dict):
            res = res['avg']
        return float(res)

    def forecast(self, src=None):
        """Return the forecast array."""
        src = src or self.data['days']
        data = []
        for entry in src:
            if entry.get('hourly') is None:
                data.append({
                    ATTR_FORECAST_TIME:
                        entry['date']['local'],
                    ATTR_FORECAST_CONDITION:
                        self.condition(entry),
                    ATTR_FORECAST_TEMP:
                        entry['temperature']['max'],
                    ATTR_FORECAST_TEMP_LOW:
                        entry['temperature']['min'],
                    ATTR_FORECAST_PRESSURE:
                        self.pressure_hpa(entry),
                    ATTR_FORECAST_HUMIDITY:
                        self.humidity(entry),
                    ATTR_FORECAST_WIND_SPEED:
                        self.wind_speed_kmh(entry),
                    ATTR_FORECAST_WIND_BEARING:
                        self.wind_bearing(entry),
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
                                self.condition(part),
                            ATTR_FORECAST_TEMP:
                                self.temperature(part),
                            ATTR_FORECAST_PRESSURE:
                                self.pressure_hpa(part),
                            ATTR_FORECAST_HUMIDITY:
                                self.humidity(part),
                            ATTR_FORECAST_WIND_SPEED:
                                self.wind_speed_kmh(part),
                            ATTR_FORECAST_WIND_BEARING:
                                self.wind_bearing(part),
                            ATTR_FORECAST_PRECIPITATION:
                                int(part['precipitation']['type'] != 0),
                        })
        return data
