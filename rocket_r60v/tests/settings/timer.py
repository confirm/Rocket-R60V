#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the auto_on setting.
'''

__all__ = (
    'TestAutoOn',
    'TestAutoOff',
)

import logging
from unittest import main

from rocket_r60v.settings import AutoOn, AutoOff

from .base import TestSetting

logging.disable()


class TestAutoOn(TestSetting):
    '''
    Test auto on setting.
    '''
    setting_class    = AutoOn
    machine_property = 'auto_on'

    def test_read(self):
        '''
        Test reading of the auto on state.
        '''
        self._test(
            'r00510002FA',
            'r005100020600C0',
            '06:00',
        )

    def test_write(self):
        '''
        Test writing of the auto on state.
        '''

        self._test(
            'w005100020600C5',
            'w00510002OK99',
            'OK',
            '06:00',
        )


class TestAutoOff(TestSetting):
    '''
    Test auto off setting.
    '''
    setting_class    = AutoOff
    machine_property = 'auto_off'

    def test_read(self):
        '''
        Test reading of the auto on state.
        '''
        self._test(
            'r00530002FC',
            'r005300021700C4',
            '23:00',
        )

    def test_write(self):
        '''
        Test writing of the auto on state.
        '''

        self._test(
            'w005300021700C9',
            'w00530002OK9B',
            'OK',
            '23:00',
        )


if __name__ == '__main__':
    main()
