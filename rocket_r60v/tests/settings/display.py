#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test case for the display setting.
'''

__all__ = (
    'TestDisplay',
)

import logging
from unittest import main

from rocket_r60v.settings import Display

from .base import TestSetting

logging.disable()


class TestDisplay(TestSetting):
    '''
    Test display setting.
    '''
    setting_class    = Display
    machine_property = 'display'

    def test_read(self):
        '''
        Test reading of the display content.
        '''
        self._test(
            'rB00700400F',
            (
                'rB0070040'
                '4252455720424F494C2E203130352A4350524553535552452050524F462E2041'
                '313A20202020362E30222020342E306248324F2054616E6B2052756E206F7574'
                '91'
            ),
            (
                'BREW BOIL. 105*C\n'
                'PRESSURE PROF. A\n'
                '1:    6.0"  4.0b\n'
                'H2O Tank Run out'
            )
        )


if __name__ == '__main__':
    main()
