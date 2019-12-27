#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the standby setting.
'''

__all__ = (
    'TestStandby',
)

import logging
from unittest import main

from rocket_r60v.settings import Standby

from .base import TestSetting

logging.disable()


class TestStandby(TestSetting):
    '''
    Test standby setting.
    '''
    setting_class    = Standby
    machine_property = 'standby'

    def test_read(self):
        '''
        Test reading of the standby state.
        '''
        self._test(
            'r004A000108',
            'r004A00010068',
            'off',
        )

        self._test(
            'r004A000108',
            'r004A00010169',
            'on',
        )

    def test_write(self):
        '''
        Test writing of the standby state.
        '''

        self._test(
            'w004A0001006D',
            'w004A0001OKA7',
            'OK',
            'off',
        )

        self._test(
            'w004A0001016E',
            'w004A0001OKA7',
            'OK',
            'on',
        )


if __name__ == '__main__':
    main()
