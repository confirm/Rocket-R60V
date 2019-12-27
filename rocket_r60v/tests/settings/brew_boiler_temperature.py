#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test case for the brew boiler temperature setting.
'''

__all__ = (
    'TestBrewBoilerTemperature',
)

from unittest import main

from rocket_r60v.settings import BrewBoilerTemperature

from .base import TestSetting


class TestBrewBoilerTemperature(TestSetting):
    setting_class    = BrewBoilerTemperature
    machine_property = 'brew_boiler_temperature'

    def test_read(self):
        '''
        Test reading of the value.
        '''
        self._test(
            'r00020001F5',
            'r000200016964',
            105,
        )

    def test_setter(self):
        '''
        Test setting of the value.
        '''
        self._test(
            'w000200016969',
            'w00020001OK94',
            'OK',
            105
        )


if __name__ == '__main__':
    main()
