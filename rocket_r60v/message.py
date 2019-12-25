'''
Rocket message module.
'''

__all__ = (
    'Message',
)

import logging
from functools import reduce

from .exceptions import ValidationError

LOGGER = logging.getLogger()


class Message:  # pylint: disable=too-many-instance-attributes
    '''
    A single message which meets the requirements of the Rocket message
    protocol.

    Here's an example message which will set the language of the machine to
    English:

    .. code-block::

        w000100010059

    +----------+----------+---------------------------------------------+----------+
    | Position |  Usage   |                 Description                 | Example  |
    +==========+==========+=============================================+==========+
    | 1        | Command  | The command.                                | ``w``    |
    |          |          | Uses ``r`` (``0x72``) for reading,          |          |
    |          |          | or ``w`` (``0x77``) for writing.            |          |
    +----------+----------+---------------------------------------------+----------+
    | 2 … 5    | Offset   | The memory offset.                          | ``0001`` |
    |          |          | Uses an 16-bit unsigned integer,            |          |
    |          |          | encoded as uppercase hex value.             |          |
    +----------+----------+---------------------------------------------+----------+
    | 6 … 9    | Length   | The data length.                            | ``0001`` |
    |          |          | Uses an 16-bit unsigned integer,            |          |
    |          |          | encoded as uppercase hex value.             |          |
    +----------+----------+---------------------------------------------+----------+
    | 10 … -2  | Data     | The data itself.                            | ``00``   |
    |          |          | Uses a sequence of 8-bit unsigned integers, |          |
    |          |          | encoded as uppercase hex values.            |          |
    +----------+----------+---------------------------------------------+----------+
    | -2 … END | Checksum | The checksum.                               | ``59``   |
    |          |          | Modulo 256 of the sum of all bytes,         |          |
    |          |          | encoded as uppercase hex value.             |          |
    +----------+----------+---------------------------------------------+----------+

    .. note::

        Please note that these are not "official" terms by Rocket itself.
        I just reverse engineered everything and tried to use matching terms all
        across my code base. Next to these terms, I'll make use of the
        following ones:

            - Raw Message: The complete message with its checksum (i.e. ``w000100010059``)
            - Message: The message without its checksum (i.e. ``w0001000100``)
            - Envelope: The command, offset & length (i.e. ``w00010001``)
    '''

    def __init__(self, command, offset, length, data='', convert_int=True):  # pylint: disable=too-many-arguments
        '''
        The message for the Rocket API.

        :param str command: The command [r|w]
        :param int offset: The memory offset
        :param int length: The data length
        :param str data: The data
        :param bool convert_int: Convert ``data`` int (base 10) to hex (base 16)
        '''
        if data != '' and convert_int:
            data = f'{data:0{length*2}X}'

        self.command     = command
        self.offset      = offset
        self.length      = length
        self.data        = str(data)[0:(length*2)]
        self.envelope    = self.build_envelope()
        self.message     = self.build_message()
        self.checksum    = self.calculate_checksum(self.message)
        self.raw_message = self.build_raw_message()

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
        command (read or write), offset & length of the message.

        :return: The envelope
        :rtype: str
        '''
        envelope = f'{self.command}{self.offset:04X}{self.length:04X}'
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
