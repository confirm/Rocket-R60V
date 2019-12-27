#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test case for the profile settings.
'''

__all__ = (
    'TestActiveProfile',
    'TestProfileA',
    'TestProfileB',
    'TestProfileC',
)

import logging
from unittest import main

from rocket_r60v.settings import ActiveProfile, ProfileA, ProfileB, ProfileC
from rocket_r60v.exceptions import SettingValueError

from .base import TestSetting

logging.disable()


class TestActiveProfile(TestSetting):
    '''
    Test active profile setting.
    '''
    setting_class    = ActiveProfile
    machine_property = 'active_profile'

    def test_read(self):
        '''
        Test reading of the active profiles.
        '''
        self._test(
            'r00470001FE',
            'r00470001005E',
            'A',
        )

        self._test(
            'r00470001FE',
            'r00470001015F',
            'B',
        )

        self._test(
            'r00470001FE',
            'r004700010260',
            'C',
        )

    def test_write(self):
        '''
        Test writing of the active profiles.
        '''
        self._test(
            'w004700010063',
            'w00470001OK9D',
            'OK',
            'A',
        )

        self._test(
            'w004700010164',
            'w00470001OK9D',
            'OK',
            'B',
        )

        self._test(
            'w004700010265',
            'w00470001OK9D',
            'OK',
            'C',
        )


class TestProfileA(TestSetting):
    '''
    Test profile A setting.
    '''
    setting_class = ProfileA
    machine_property = 'profile_a'

    def test_read(self):
        '''
        Test reading of the profile.
        '''
        self._test(
            'r0016000F0F',
            'r0016000F3C00B4003C0000000000285A32000016',
            '6:4 18:9 6:5 0:0 0:0',
        )

    def test_write(self):
        '''
        Test writing of the profile.
        '''
        self._test(
            'w0016000F3C00B4003C0000000000285A3200001B',
            'w0016000FOKAE',
            'OK',
            '6:4 18:9 6:5 0:0 0:0',
        )

    def test_incomplete_profile(self):
        '''
        Test writing of incomplete profile.
        '''
        self._test(
            'w0016000F3C00B4003C0000000000285A3200001B',
            'w0016000FOKAE',
            'OK',
            '6:4 18:9 6:5',
        )

    def test_invalid_profiles(self):
        '''
        Test writing of invalid profile.
        '''
        with self.assertRaises(SettingValueError):
            ProfileA(None).set('1:2 2:3 3:x')


class TestProfileB(TestSetting):
    '''
    Test profile B setting.
    '''
    setting_class = ProfileB
    machine_property = 'profile_b'

    def test_read(self):
        '''
        Test reading of the profile.
        '''
        self._test(
            'r0026000F10',
            'r0026000F5000DC00000000000000285A000000FC',
            '8:4 22:9 0:0 0:0 0:0',
        )

    def test_write(self):
        '''
        Test writing of the profile.
        '''
        self._test(
            'w0026000F5000DC00000000000000285A00000001',
            'w0026000FOKAF',
            'OK',
            '8:4 22:9 0:0 0:0 0:0',
        )


class TestProfileC(TestSetting):
    '''
    Test profile B setting.
    '''
    setting_class = ProfileC
    machine_property = 'profile_c'

    def test_read(self):
        '''
        Test reading of the profile.
        '''
        self._test(
            'r0036000F11',
            'r0036000FC80064000000000000005A32000000F1',
            '20:9 10:5 0:0 0:0 0:0',
        )

    def test_write(self):
        '''
        Test writing of the profile.
        '''
        self._test(
            'w0036000FC80064000000000000005A32000000F6',
            'w0036000FOKB0',
            'OK',
            '20:9 10:5 0:0 0:0 0:0',
        )


if __name__ == '__main__':
    main()
