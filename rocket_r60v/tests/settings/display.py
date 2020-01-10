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
            'rB00700300E',
            'rB00700304252455720424F494C2E203130352A4350524553535552452050524' \
            'F462E2041313A20202020362E30222020342E3062BB',
            'BREW BOIL. 105*C\nPRESSURE PROF. A\n1:    6.0"  4.0b',
        )


if __name__ == '__main__':
    main()
