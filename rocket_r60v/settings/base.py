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

    def send(self, command, data=[]):
        '''
        Send a message to the machine.

        :param str command: The command [r|w]
        :param list data: The data sequence

        :retrun: The response data
        :rtype: str
        '''
        message = Message(
            command=command,
            offset=self.offset,
            length=self.length,
            data=data,
        )

        return self.machine.send_message(message)

    def get(self):
        '''
        Get the setting value from the machine.

        :return: The setting value
        :rtype: mixed
        '''
        LOGGER.debug('Getting value for %s…', self.__class__.__name__)
        return self.send(command='r')


class WritableSetting(ReadOnlySetting):  # pylint: disable=abstract-method
    '''
    A writable setting from which all other writable settings should inherit.
    '''

    def set(self, data):
        '''
        Set the setting value on the machine.

        :param list data: The data sequence

        :return: The received data
        :rtype: str

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''

        LOGGER.debug('Setting value for %s to "%s"…', self.__class__.__name__, data)

        data = self.send(command='w', data=data)

        if data[0] != 'OK':
            error = 'Expected response data was "OK", got "%s" instead'
            LOGGER.error(error, data)
            raise ValidationError(error % data)

        return data[0]


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
            index  = super().get(*args, **kwargs)[0]
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

        index = self.choices.index(choice)
        LOGGER.debug('Selected choice for %s of is "%s", equals to value "%s"…',
                     self.__class__.__name__, choice, index)

        return super().set([index], *args, **kwargs)


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
        return self.validate_value(super().get(*args, **kwargs)[0])

    def set(self, value, *args, **kwargs):  # pylint: disable=arguments-differ
        '''
        Set the setting value on the machine.

        :param str data: The setting value

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        value = int(value)
        return super().set([self.validate_value(value)], *args, **kwargs)
