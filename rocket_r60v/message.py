'''
Rocket message module.
'''

__all__ = (
    'Message',
)

import logging
from functools import reduce

from .exceptions import ValidationError, MessageLengthError

LOGGER = logging.getLogger()


class Message:  # pylint: disable=too-many-instance-attributes
    '''
    A single message which meets the requirements of the Rocket message
    protocol.

    Please have a look at the REVERSE_ENGINEERING.rst document for more
    informations about the Rocket message protocol.
    '''

    def __init__(self, command, address, length, data=None, encode_data=True):  # pylint: disable=too-many-arguments
        '''
        The message for the Rocket API.

        :param str command: The commanfd [r|w]
        :param int address: The memory address
        :param int length: The data length
        :param data: The data sequence
        :type data: None, str, int or list
        :param bool encode_data: Encode ``data`` sequence integers (base 10) to hex (base 16)
        '''
        if encode_data:
            data = self.encode_data(data)

        if command == 'w' and len(data) != length * 2:
            error = 'Invalid length (%d) defiend for data "%s"'
            LOGGER.error(error, length, data)
            raise MessageLengthError(error % (length, data))

        self.command     = command
        self.address     = address
        self.length      = length
        self.data        = data
        self.envelope    = self.build_envelope()
        self.message     = self.build_message()
        self.checksum    = self.calculate_checksum(self.message)
        self.raw_message = self.build_raw_message()

    @classmethod
    def encode_data(cls, data):
        '''
        Encode the data sequence into a message compitable sequence of hex
        values (base 16).

        :param data: The data sequence
        :type data: None, str, int or list

        :return: The data string
        :rtype: str
        '''
        if data is None:
            return ''

        if isinstance(data, str):
            data = [int(data)]
        elif isinstance(data, int):
            data = [data]

        return ''.join((f'{x:02X}' for x in data))

    @classmethod
    def decode_data(cls, message):
        '''
        Decode the data of a message, from a hex (base 16) into an integer
        (base 10) sequence.

        :param str message: The message string

        :return: The data list
        :rtype: list
        '''
        length  = int(message[5:9], 16)
        encoded = message[9:(9 + length * 2)]
        decoded = []

        LOGGER.debug('Encoded data is "%s"', encoded)

        if encoded[:2] == 'OK':
            LOGGER.debug('Decoding skipped as "OK" was returned…')
            return ['OK']

        for i in range(0, length * 2, 2):
            start = i
            end   = start + 2
            decoded.append(int(encoded[start:end], 16))

        LOGGER.debug('Decoded data is "%s"', decoded)

        return decoded

    @classmethod
    def calculate_checksum(cls, message):
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

    def build_envelope(self):
        '''
        Build the message envelope.

        The envelope is the first 9 bytes of the message and contains the
        command (read or write), address & length of the message.

        :return: The envelope
        :rtype: str
        '''
        envelope = f'{self.command}{self.address:04X}{self.length:04X}'
        LOGGER.debug('Message envelope is "%s"', envelope)
        return envelope

    def build_message(self):
        '''
        Build the message.

        The message is the data which is sent via TCP except its checksum. It
        consists of the envelope & the actual (Rocket) data.

        .. seealso:

            Method :py:meth:`build_envelope`
                The format of the message envelope

        :return: The message without its checksum
        :rtype: str
        '''
        message  = f'{self.envelope}{self.data}'
        LOGGER.debug('Message is "%s"', message)
        return message

    def build_raw_message(self):
        '''
        Build the raw message.

        The raw message is the message which is sent via TCP including its
        checksum.

        .. seealso:

            Method :py:meth:`build_message`
                The message itself

            Method :py:meth:`calculate_checksum`
                The calculation of the message checksum

        :return: The message with its checksum
        :rtype: str
        '''
        raw_message = f'{self.message}{self.checksum}'
        LOGGER.debug('Raw message is "%s"', raw_message)
        return raw_message

    def validate_response(self, response_message):
        '''
        Validate the response message.

        This is achieved by making sure its message envelope matches the
        envelope of the request message, and by validating the checksum.

        :param str response_message: The raw response message

        :raises rocket.exceptions.ValidationError: When the validation fails
        '''
        response_envelope = response_message[0:9]
        if response_envelope != self.envelope:
            error = 'Invalid response envelope, exepcted "%s", got "%s"'
            LOGGER.error(error, self.envelope, response_envelope)
            raise ValidationError(error % (self.envelope, response_envelope))

        response_checksum   = response_message[-2:]
        calculated_checksum = self.calculate_checksum(response_message[0:-2])
        if response_checksum != calculated_checksum:
            error = 'Invalid response checksum, exepcted "%s", got "%s"'
            LOGGER.error(error, calculated_checksum, response_checksum)
            raise ValidationError(error % (calculated_checksum, response_checksum))

        LOGGER.debug('Raw response message "%s" validated successfully', response_message)

    def encode(self):
        '''
        The encoded version of the message string.

        :return: The encoded string
        :rtype: bytes
        '''
        return self.raw_message.encode()

    def __str__(self):
        '''
        Return string representation of this message.

        :return: The message string
        :rtype: str
        '''
        return self.raw_message
