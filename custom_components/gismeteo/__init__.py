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

from .const import VERSION


class TestLogger():
    @staticmethod
    def debug(format, *args):
        print('[DEBUG] ' + format % args)

    @staticmethod
    def warning(format, *args):
        print('[WARNING] ' + format % args)

    @staticmethod
    def error(format, *args):
        print('[ERROR] ' + format % args)
