'''
Base setting module.
'''

__all__ = (
    'ReadOnlySetting',
    'WritableSetting',
    'ChoiceSetting',
    'RangeSetting',
)

import logging

from rocket_r60v.message import Message
from rocket_r60v.exceptions import ValidationError, SettingValueError

LOGGER = logging.getLogger(__name__)


class ReadOnlySetting:
    '''
    A read-only setting and the base setting from which all other settings
    should inherit.
    '''
    length = 1

    @property
    def offset(self):
        '''
        The memory offset.

        :return: The memory offset
        :rtype: int
        '''
        raise NotImplementedError('Offset property not implemented')

    def __init__(self, machine):
        '''
        Constructor.

        :param rocket.machine.Machine: The machine instance
        '''
        self.machine = machine

    def send(self, command, data=''):
        '''
        Send a message to the machine.

        :param str command: The command [r|w]
        :param str data: The data

        :retrun: The response data
        :rtype: str
        '''
        message = Message(
            command=command,
            offset=self.offset,
            length=self.length,
            data=data
        )

        return self.machine.send_message(message)

    def get(self, convert_int=True):
        '''
        Get the setting value from the machine.

        :param bool convert_int: Convert received hex value (base 16) to int (base 10)

        :return: The setting value
        :rtype: mixed
        '''
        LOGGER.debug('Getting value for %s…', self.__class__.__name__)
        data = self.send('r')
        return int(data, 16) if convert_int else data


class WritableSetting(ReadOnlySetting):  # pylint: disable=abstract-method
    '''
    A writable setting from which all other writable settings should inherit.
    '''

    def set(self, data, convert_int=True):
        '''
        Set the setting value on the machine.

        :param str data: The setting value
        :param bool convert_int: Convert received int value (base 10) to hex (base 16)

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        if convert_int:
            length = 2 * self.length
            data   = f'{data:0{length}X}'

        LOGGER.debug('Setting value for %s to "%s"…', self.__class__.__name__, data)

        data = self.send('w', data)
        if data != 'OK':
            error = 'Expected response data was "OK", got "%s" instead'
            LOGGER.error(error, data)
            raise ValidationError(error % data)

    def set_cli_value(self, argument):
        '''
        Parse the CLI argument and set it on the machine.
        '''
        self.set(argument)


class ChoiceSetting(WritableSetting):
    '''
    Setting which uses an index based list of choices.
    '''

    @property
    def choices(self):
        '''
        The choices.

        :return: The choices
        :rtype: tuple

        :raises NotImplementedError: When not implemented
        '''
        raise NotImplementedError('Choices property not implemented')

    def get(self, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Get the choice setting value from the machine.

        :return: The setting choice
        :rtype: str
        '''
        try:
            index  = super().get(*args, **kwargs)
            choice = self.choices[index]
            LOGGER.info('Choice of %s is "%s"', self.__class__.__name__, choice)
            return choice
        except IndexError:
            error = 'Unknown choice (#%d) on machine'
            LOGGER.error(error, index)
            raise SettingValueError(error % index)

    def set(self, choice, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the setting value on the machine on a specific choice.

        :param str choice: The name of the choice

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        if choice not in self.choices:
            error = 'Invalid choice "%s", valid choises are "%s"'
            LOGGER.error(error, choice, self.choices)
            raise SettingValueError(error % (choice, self.choices))

        LOGGER.debug('Setting value for %s to choice "%s"…', self.__class__.__name__, choice)
        super().set(self.choices.index(choice))


class RangeSetting(WritableSetting):
    '''
    Setting which uses a valid integer range.
    '''

    @property
    def range(self):
        '''
        The valid range.

        :return: The range
        :rtype: tuple

        :raises NotImplementedError: When not implemented
        '''
        raise NotImplementedError('Range property not implemented')

    def validate_value(self, value):
        '''
        Validate if value is in valid range.

        :param str value: The value

        :return: The value
        :rtype: int

        :raises AssertionError: When value is not in valid range
        '''
        min_value, max_value = self.range
        try:
            assert min_value <= value <= max_value
        except AssertionError:
            error = 'Value "%d" is not in valid range [%d-%d]'
            LOGGER.error(error, value, min_value, max_value)
            raise SettingValueError(error % (value, min_value, max_value))

        return value

    def get(self, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Get the setting value from the machine.

        :return: The value
        :rtype: str
        '''
        return self.validate_value(super().get(*args, **kwargs))

    def set(self, value, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the setting value on the machine.

        :param str data: The setting value

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        super().set(self.validate_value(value), *args, **kwargs)
