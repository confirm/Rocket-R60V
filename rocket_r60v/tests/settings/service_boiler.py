#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the service boiler settings.
'''

__all__ = (
    'TestServiceBoiler',
    'TestServiceBoilerTemperature',
    'TestCurrentServiceBoilerTemperature',
)

import logging
from unittest import main

from rocket_r60v.settings import ServiceBoiler, ServiceBoilerTemperature, \
    CurrentServiceBoilerTemperature

from .base import TestSetting

logging.disable()


class TestServiceBoiler(TestSetting):
    '''
    Test service boiler setting.
    '''
    setting_class    = ServiceBoiler
    machine_property = 'service_boiler'

    def test_read(self):
        '''
        Test reading of the service boiler state.
        '''
        self._test(
            'r0049000100',
            'r004900010060',
            'off',
        )

        self._test(
            'r0049000100',
            'r004900010161',
            'on',
        )

    def test_write(self):
        '''
        Test writing of the service boiler state.
        '''

        self._test(
            'w004900010065',
            'w00490001OK9F',
            'OK',
            'off',
        )

        self._test(
            'w004900010166',
            'w00490001OK9F',
            'OK',
            'on',
        )


class TestServiceBoilerTemperature(TestSetting):
    '''
    Test service boiler temperature setting.
    '''
    setting_class    = ServiceBoilerTemperature
    machine_property = 'service_boiler_temperature'

    def test_read(self):
        '''
        Test reading of the service boiler temperature.
        '''
        self._test(
            'r00030001F6',
            'r000300017B6F',
            123,
        )

    def test_setter(self):
        '''
        Test setting of the service boiler temperature.
        '''
        self._test(
            'w000300017B74',
            'w00030001OK95',
            'OK',
            123,
        )


class TestCurrentServiceBoilerTemperature(TestSetting):
    '''
    Test current service boiler temperature setting.
    '''
    setting_class    = CurrentServiceBoilerTemperature
    machine_property = 'current_service_boiler_temperature'

    def test_read(self):
        '''
        Test reading of the service boiler temperature.
        '''
        self._test(
            'rB001000106',
            'rB00100017B7F',
            123,
        )


if __name__ == '__main__':
    main()
