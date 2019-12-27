'''
Pressure profile settings.
'''

__all__ = (
    'ActiveProfile',
    'ProfileA',
    'ProfileB',
    'ProfileC',
)

import logging

from rocket_r60v.exceptions import SettingValueError

from .base import WritableSetting, ChoiceSetting


LOGGER = logging.getLogger(__name__)


class ActiveProfile(ChoiceSetting):
    '''
    The active pressure profile.
    '''
    address = 71

    choices = (
        'A',
        'B',
        'C',
    )


class ProfileA(WritableSetting):
    '''
    The pressure profile A.
    '''
    address = 22

    length = 15

    timing_range   = (0, 60)
    pressure_range = (0, 10)

    @classmethod
    def validate_value_range(cls, name, value, value_range):
        '''
        Validate a value and return type-cast it to float.

        :param str name: The name of the value
        :param int value: The value
        :param tuple value_range: The min & max values

        :return: The value
        :rtype: float

        :raises rocket.exceptions.SettingValueError: When timing or pressure not in valid range
        '''
        min_value, max_value = value_range

        try:
            value = round(float(value), 1)

            # Use int whenever possible to improve readability.
            if str(value)[-2:] == '.0':
                value = int(value)

            assert min_value <= value <= max_value

        except (AssertionError, ValueError):
            error = 'Step %s "%s" is not a number or not in valid range [%.1f-%.1f]'
            LOGGER.error(error, name, value, min_value, max_value)
            raise SettingValueError(error % (name, value, min_value, max_value))

        return value

    def validate_step(self, timing, pressure):
        '''
        Validate the timing and pressure of a step.

        :param int timing: Seconds
        :param int pressure: Bar

        :return: The timing and pressure
        :type: tuple

        :raises rocket.exceptions.SettingValueError: When timing or pressure not in valid range
        '''
        timing   = self.validate_value_range('timing', timing, self.timing_range)
        pressure = self.validate_value_range('pressure', pressure, self.pressure_range)

        return timing, pressure

    def build_steps_from_data(self, data):
        '''
        Build steps out of received data.

        Each pressure profile has 5 steps, each with a timing (seconds) and a
        pressure (bar) value.

        The timing is stored in the first 10 data sequence items, the pressure
        in the last 5 data sequence items. As each value has a precision of .1
        (deciseconds, decibar), the data values are multiplied by 10. Thus,
        an integer base-10 value of 95 is actually 9.5 (seconds or bar).

        As mentioned before, the timing is stored in the first 10 data sequence
        items. This is because of the limitation of an 8-bit integer. Each step
        takes up to 60 seconds (i.e. 600), but an 8-bit integer can only
        reflect 25.5 seconds (i.e. 255 / 0xFF). Therefor two 8-bit integers in a
        row are used for the seconds. The second integer reflects the modulo
        256 of the total seconds, the first integer contains the rest of the
        modulo.

        :param list data: The received data

        :return: The steps
        :rtype: generator
        '''
        for i in range(0, 5):
            timing = ((data[0 + i * 2]) + (data[1 + i * 2] * 256)) / 10
            pressure = data[10 + i] / 10
            yield self.validate_step(timing, pressure)

    def get(self, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Get the pressure profile from the machine.

        :return: The pressure profile
        :rtype: str
        '''
        data = super().get(*args, **kwargs)
        data = [f'{x[0]}:{x[1]}' for x in self.build_steps_from_data(data)]
        return ' '.join(data)

    def set(self, profile, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the pressure profile on the machine.

        :param str profile: The pressure profile

        :raises rocket.exceptions.SettingValueError: When an invalid choice is selected
        '''
        steps   = str(profile).strip().split(' ')
        count   = len(steps)
        profile = []

        try:
            assert 1 <= count <= 5

            for step in steps:
                values = step.split(':')
                assert len(values) == 2
                profile.append(self.validate_step(*values))

        except AssertionError:
            error = 'Invalid pressure profile format "%s", valid format is 5x "{timing}:{pressure}"'
            LOGGER.error(error, profile)
            raise SettingValueError(error % profile)

        timing_data = []
        pressure_data     = []

        for i in range(0, 5):
            try:
                timing, pressure = profile[i]
                timing_data.extend((int(timing * 10 % 256), int(timing / 25.6)))
                pressure_data.append(int(pressure * 10))
            except IndexError:
                timing_data.extend((0, 0))
                pressure_data.append(0)

        return super().set(timing_data + pressure_data, *args, **kwargs)


class ProfileB(ProfileA):
    '''
    The pressure profile B.
    '''

    address = 38


class ProfileC(ProfileA):
    '''
    The pressure profile C.
    '''

    address = 54
