'''
Auto on setting.
'''

__all__ = (
    'AutoOn',
    'AutoStandby',
)

import logging

from .base import Setting
from rocket_r60v.exceptions import SettingValueError

LOGGER = logging.getLogger(__name__)


class Timer(Setting):
    '''
    Base timer class which handles time based values.
    '''

    def get(self):
        '''
        Get the time value from the machine.

        The time is sent in 4 bytes. The first two bytes are the our in hex,
        the second two bytes are the minute in hex.

        :return: The time
        :rtype: str
        '''
        time   = super().get(convert_int=False)
        hour   = int(time[:2], 16)
        minute = int(time[2:], 16)
        return f'{hour:02d}:{minute:02d}'

    def set(self, time):
        '''
        Set the time on the machine.

        :param str time: The time
        '''
        try:
            hour, minute = time.split(':')
            hour         = int(hour)
            minute       = int(minute)
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59
            super().set(data=f'{hour:02X}{minute:02X}', convert_int=False)

        except (ValueError, AssertionError):
            error = 'Value "%s" is not in valid time (HH:MM)'
            LOGGER.error(error, time)
            raise SettingValueError(error % time)


class AutoOn(Timer):
    '''
    The auto on time.
    '''
    offset = 81
    length = 2


class AutoStandby(Timer):
    '''
    The auto on time.
    '''
    offset = 83
    length = 2
