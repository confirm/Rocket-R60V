'''
Timer settings.
'''

__all__ = (
    'AutoOn',
    'AutoOff',
)

import logging

from rocket_r60v.exceptions import SettingValueError

from .base import WritableSetting

LOGGER = logging.getLogger(__name__)


class AutoOn(WritableSetting):
    '''
    The auto on time.
    '''
    address = 81
    length = 2

    def get(self, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Get the time value from the machine.

        The time is sent in 4 bytes. The first two bytes are the hour in hex,
        the second two bytes are the minute in hex.

        :return: The time
        :rtype: str
        '''
        hour, minute = super().get(*args, **kwargs)
        return f'{hour:02d}:{minute:02d}'

    def set(self, time, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the time on the machine.

        :param str time: The time
        '''
        try:
            hour, minute = str(time).split(':')
            hour         = int(hour)
            minute       = int(minute)
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59
            return super().set([hour, minute], *args, **kwargs)

        except (ValueError, AssertionError):
            error = 'Value "%s" is not in valid time (HH:MM)'
            LOGGER.error(error, time)
            raise SettingValueError(error % time)


class AutoOff(AutoOn):
    '''
    The auto off (standby) time.
    '''
    address = 83
    length = 2
