'''
Date & time settings.
'''

__all__ = (
    'DateTime',
)

import logging
from time import localtime, strptime

from rocket_r60v.exceptions import SettingValueError

from .base import WritableSetting

LOGGER = logging.getLogger(__name__)


class DateTime(WritableSetting):
    '''
    The date & time (clock) of the machine.
    '''
    address = 0xA000
    length  = 7

    def get(self, *args, **kwargs):  # pylint: disable=arguments-differ,unused-argument
        '''
        The date & time can't be read, therefor an error is printed.

        :return: The time
        :rtype: str
        '''
        return f'The date & time can only be set and not read ("fire & forget" if you will so).'

    def set(self, date_and_time, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the date & time.

        :param str time: The time
        '''
        try:
            if date_and_time == 'auto':
                time_struct = localtime()
            else:
                time_struct = strptime(date_and_time, '%d.%m.%y %H:%M')

            day      = time_struct.tm_mday
            month    = time_struct.tm_mon
            year     = time_struct.tm_year - 2000
            weekday  = time_struct.tm_wday + 1
            hour     = time_struct.tm_hour
            minute   = time_struct.tm_min

            return super().set([0, minute, hour, weekday, day, month, year], *args, **kwargs)

        except (ValueError, TypeError) as ex:
            error = 'Value "%s" is not a valid date & time format (auto | dd.mm.yy HH:MM)'
            LOGGER.error(error, date_and_time)
            raise SettingValueError(error % date_and_time) from ex
