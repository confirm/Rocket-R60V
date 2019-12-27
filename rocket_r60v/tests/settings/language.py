#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test case for the language setting.
'''

__all__ = (
    'TestLanguage',
)

import logging
from unittest import main

from rocket_r60v.settings import Language

from .base import TestSetting

logging.disable()


class TestLanguage(TestSetting):
    '''
    Test language setting.
    '''
    setting_class    = Language
    machine_property = 'language'

    def test_read(self):
        '''
        Test reading of the languages.
        '''
        self._test(
            'r00010001F4',
            'r000100010054',
            'English',
        )

        self._test(
            'r00010001F4',
            'r000100010155',
            'German',
        )

        self._test(
            'r00010001F4',
            'r000100010256',
            'French',
        )

        self._test(
            'r00010001F4',
            'r000100010357',
            'Italian',
        )

    def test_write(self):
        '''
        Test writing of the languages.
        '''
        self._test(
            'w000100010059',
            'w00010001OK93',
            'OK',
            'English',
        )

        self._test(
            'w00010001015A',
            'w00010001OK93',
            'OK',
            'German',
        )

        self._test(
            'w00010001025B',
            'w00010001OK93',
            'OK',
            'French',
        )

        self._test(
            'w00010001035C',
            'w00010001OK93',
            'OK',
            'Italian',
        )


if __name__ == '__main__':
    main()
