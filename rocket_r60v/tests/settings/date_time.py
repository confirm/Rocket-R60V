#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the date_time setting.
'''

__all__ = (
    'TestDateTime',
)

import logging
from unittest import main
from time import localtime

from rocket_r60v.settings import DateTime
from rocket_r60v.message import Message

from .base import TestSetting

logging.disable()


class TestDateTime(TestSetting):
    '''
    Test auto on setting.
    '''
    setting_class    = DateTime
    machine_property = 'date_time'

    def test_write(self):
        '''
        Test writing of the date & time.
        '''

        self._test(
            'wA000000700211503130214C6',
            'wA0000007OKA9',
            'OK',
            '19.2.20 21:33',
        )

        time_struct = localtime()
        day      = time_struct.tm_mday
        month    = time_struct.tm_mon
        year     = time_struct.tm_year - 2000
        weekday  = time_struct.tm_wday + 1
        hour     = time_struct.tm_hour
        minute   = time_struct.tm_min
        message  = f'wA000000700{minute:02X}{hour:02X}{weekday:02X}{day:02X}{month:02X}{year:02X}'
        checksum = Message.calculate_checksum(message)

        self._test(
            f'{message}{checksum}',
            'wA0000007OKA9',
            'OK',
            'auto',
        )


if __name__ == '__main__':
    main()
