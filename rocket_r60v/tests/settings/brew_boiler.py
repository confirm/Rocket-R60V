#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the brew boiler setting.
'''

__all__ = (
    'TestBrewBoilerTemperature',
    'TestCurrentBrewBoilerTemperature',
)

import logging
from unittest import main

from rocket_r60v.settings import BrewBoilerTemperature, CurrentBrewBoilerTemperature

from .base import TestSetting

logging.disable()


class TestBrewBoilerTemperature(TestSetting):
    '''
    Test brew boiler temperature setting.
    '''
    setting_class    = BrewBoilerTemperature
    machine_property = 'brew_boiler_temperature'

    def test_read(self):
        '''
        Test reading of the brew boiler temperature.
        '''
        self._test(
            'r00020001F5',
            'r000200016964',
            105,
        )

    def test_setter(self):
        '''
        Test setting of the brew boiler temperature.
        '''
        self._test(
            'w000200016969',
            'w00020001OK94',
            'OK',
            105
        )


class TestCurrentBrewBoilerTemperature(TestSetting):
    '''
    Test current brew boiler temperature setting.
    '''
    setting_class    = CurrentBrewBoilerTemperature
    machine_property = 'current_brew_boiler_temperature'

    def test_read(self):
        '''
        Test reading of the brew boiler temperature.
        '''
        self._test(
            'rB000000105',
            'rB00000016974',
            105,
        )


if __name__ == '__main__':
    main()
