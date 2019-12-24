'''
Base setting module.
'''

__all__ = (
    'Setting',
    'ChoiceSetting',
    'RangeSetting',
)

import logging
from functools import reduce

from rocket.exceptions import ValidationError, SettingValueError

LOGGER = logging.getLogger(__name__)


class Setting:
    '''
    The base setting from which all other settings should inherit.
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

    @staticmethod
    def calculate_checksum(message):
        '''
        Calculate the checksum of the message.

        The checksum for the message is calculated by summarising the value of
        all bytes in the message, followed by a modulo 256 and a conversion into
        its hexadecimal value.

        :param str message: The message (w/o checksum)

        :return: The hexadecimal checksum
        :rtype: str
        '''
        checksum = reduce(lambda x, y: x + y, message.encode()) % 256
        checksum = f'{checksum:02X}'
        LOGGER.debug('Calculated checksum is "%s"', checksum)

        return checksum

    def validate_response(self, request_message, response_message):
        '''
        Validate the response message.

        This is achieved by making sure its message envelope matches the
        envelope of the request message, and by validating the checksum.

        :param str request_message: The raw request message
        :param str response_message: The raw response message

        :raises rocket.exceptions.ValidationError: When the validation fails
        '''
        request_envelope  = request_message[0:9]
        response_envelope = response_message[0:9]
        if request_envelope != response_envelope:
            error = 'Invalid response envelope, exepcted "%s", got "%s"'
            LOGGER.error(error, request_envelope, response_envelope)
            raise ValidationError(error % (request_envelope, response_envelope))

        response_checksum   = response_message[-2:]
        calculated_checksum = self.calculate_checksum(response_message[0:-2])
        if response_checksum != calculated_checksum:
            error = 'Invalid response checksum, exepcted "%s", got "%s"'
            LOGGER.error(error, calculated_checksum, response_checksum)
            raise ValidationError(error % (calculated_checksum, response_checksum))

        LOGGER.debug('Raw response message "%s" validated successfully', response_message)

    def build_envelope(self, command):
        '''
        Build the message envelope.

        The envelope is the first 9 bytes of the message and contains the
        command (read or write), offset & length of the message.

        :param str command: The command [r|w]

        :return: The envelope
        :rtype: str
        '''
        envelope = f'{command}{self.offset:04X}{self.length:04X}'
        LOGGER.debug('Envelope is "%s"', envelope)
        return envelope

    def build_raw_message(self, command, data=''):
        '''
        Build the raw message.

        The raw message is the data which is sent via TCP. It consists of the
        envelope, the actual (Rocket) data and a checksum.

        .. seealso:

            Method :py:meth:`build_envelope`
                The format of the message envelope

            Method :py:meth:`calculate_checksum`
                The calculation of the message checksum

        :param str command: The command [r|w]
        :param str data: The data

        :return: The message with checksum
        :rtype: str
        '''
        envelope = self.build_envelope(command)
        message  = f'{envelope}{data}'
        LOGGER.debug('Message is "%s"', message)

        checksum    = self.calculate_checksum(message)
        raw_message = f'{message}{checksum}'
        LOGGER.debug('Raw message is "%s"', raw_message)

        return raw_message

    def send(self, command, data=''):
        '''
        Send a message to the machine.

        :param str command: The command [r|w]
        :param str data: The data

        :retrun: The response data
        :rtype: str
        '''
        request  = self.build_raw_message(command, data)
        response = self.machine.send(request)

        self.validate_response(request, response)

        data = response[9:-2]
        LOGGER.info('Received data is "%s"', data)
        return data

    def get(self):
        '''
        Get the setting value from the machine.

        :return: The setting value
        :rtype: mixed
        '''
        LOGGER.debug('Getting value for %s…', self.__class__.__name__)
        return int(self.send('r'), 16)

    def set(self, data):
        '''
        Set the setting value on the machine.

        :param str data: The setting value

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        data = f'{data:02X}'
        LOGGER.debug('Setting value for %s to "%s"…', self.__class__.__name__, data)

        data = self.send('w', data)
        if data != 'OK':
            error = 'Expected response data was "OK", got "%s" instead'
            LOGGER.error(error, data)
            raise ValidationError(error % data)


class ChoiceSetting(Setting):
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

    def get(self):
        '''
        Get the choice setting value from the machine.

        :return: The setting choice
        :rtype: str
        '''
        try:
            index  = super().get()
            choice = self.choices[index]
            LOGGER.info('Choice of %s is "%s"', self.__class__.__name__, choice)
            return choice
        except IndexError:
            error = 'Unknown choice (#%d) on machine'
            LOGGER.error(error, index)
            raise SettingValueError(error % index)

    def set(self, choice):  # pylint: disable=arguments-differ
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


class RangeSetting(Setting):
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

    def get(self):
        '''
        Get the setting value from the machine.

        :return: The value
        :rtype: str
        '''
        return self.validate_value(super().get())

    def set(self, value):  # pylint: disable=arguments-differ
        '''
        Set the setting value on the machine.

        :param str data: The setting value

        :raises rocket.exceptions.ValidationError: When response data isn't "OK"
        '''
        super().set(self.validate_value(value))
