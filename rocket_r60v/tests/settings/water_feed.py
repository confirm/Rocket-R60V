#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the water feed setting.
'''

__all__ = (
    'TestWaterFeed',
)

import logging
from unittest import main

from rocket_r60v.settings import WaterFeed

from .base import TestSetting

logging.disable()


class TestWaterFeed(TestSetting):
    '''
    Test water feed setting.
    '''
    setting_class    = WaterFeed
    machine_property = 'water_feed'

    def test_read(self):
        '''
        Test reading of the water feed.
        '''
        self._test(
            'r00460001FD',
            'r00460001005D',
            'HardPlumbed',
        )

        self._test(
            'r00460001FD',
            'r00460001015E',
            'Reservoir',
        )

    def test_setter(self):
        '''
        Test setting of the water feed.
        '''
        self._test(
            'w004600010062',
            'w00460001OK9C',
            'OK',
            'HardPlumbed',
        )

        self._test(
            'w004600010163',
            'w00460001OK9C',
            'OK',
            'Reservoir',
        )


if __name__ == '__main__':
    main()
