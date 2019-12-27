#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test case for the count setting.
'''

__all__ = (
    'TestTotalCoffeeCount',
)

import logging
from unittest import main

from rocket_r60v.settings import TotalCoffeeCount

from .base import TestSetting

logging.disable()


class TestTotalCoffeeCount(TestSetting):
    '''
    Test total coffee count setting.
    '''
    setting_class    = TotalCoffeeCount
    machine_property = 'total_coffee_count'

    def test_read(self):
        '''
        Test reading of the total coffee count.
        '''
        self._test(
            'r004D00010B',
            'r004D00018C86',
            140,
        )


if __name__ == '__main__':
    main()
