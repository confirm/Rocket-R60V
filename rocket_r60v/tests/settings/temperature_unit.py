#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the temperature_unit setting.
'''

__all__ = (
    'TestTemperatureUnit',
)

import logging
from unittest import main

from rocket_r60v.settings import TemperatureUnit

from .base import TestSetting

logging.disable()


class TestTemperatureUnit(TestSetting):
    '''
    Test temperature unit setting.
    '''
    setting_class    = TemperatureUnit
    machine_property = 'temperature_unit'

    def test_read(self):
        '''
        Test reading of the temperature unit state.
        '''
        self._test(
            'r00000001F3',
            'r000000010053',
            'Celsius',
        )

        self._test(
            'r00000001F3',
            'r000000010154',
            'Fahrenheit',
        )

    def test_write(self):
        '''
        Test writing of the temperature unit state.
        '''

        self._test(
            'w000000010058',
            'w00000001OK92',
            'OK',
            'Celsius',
        )

        self._test(
            'w000000010159',
            'w00000001OK92',
            'OK',
            'Fahrenheit',
        )


if __name__ == '__main__':
    main()
