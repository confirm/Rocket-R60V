'''
Rocket API module.
'''

__all__ = (
    'API',
)

import logging
import socket

from .exceptions import RocketConnectionError
from .message import Message

LOGGER = logging.getLogger(__name__)


class API:
    '''
    API class which can be used to connect and interact with the Rocket R60V.
    '''
    buffer_size = 1024
    retries     = 3

    def __init__(self, address='192.168.1.1', port=1774, timeout=3.0):
        '''
        Constructor.

        :param str address: The IP address of the machine
        :param int port: The port number of the machine
        :param int buffer_size: The TCP buffer size
        '''
        self.address  = address
        self.port     = port
        self.timeout  = timeout
        self.socket  = None

    def __del__(self):
        '''
        Destructor.
        '''
        self.disconnect()

    def connect(self):
        '''
        Connect to the machine.
        '''
        address = self.address
        port    = self.port
        timeout = self.timeout

        LOGGER.info('Connecting to %s:%d…', address, port)

        try:
            self.socket = socket.create_connection((address, port), timeout)
        except socket.timeout as ex:
            error = 'Connection to %s:%d failed'
            LOGGER.error(error, address, port)
            raise RocketConnectionError(error % (address, port)) from ex

        data = self.read()

        if data != '*HELLO*':
            error = 'Machine didn\'t say hello ("%s"), connection failed'
            LOGGER.error(error, data)
            raise RocketConnectionError(error % data)

        LOGGER.info('Connected to %s:%d', address, port)

    def disconnect(self):
        '''
        Disconnect from the machine.
        '''
        if self.socket is not None:
            self.socket.close()

    def read(self):
        '''
        Read data from the socket.

        :return: The data
        :rtype: str
        '''
        LOGGER.debug('Reading…')
        data = self.socket.recv(self.buffer_size).decode()
        LOGGER.debug('Received raw message is "%s"', data)
        return data

    def send_message(self, message, attempt=1):
        '''
        Send data (i.e. raw message) to the machine and wait for response.

        :param rocket_r60v.message.Message message: The message
        :param int attempt: The attempt counter

        :return: The received data
        :rtype: list
        '''
        LOGGER.debug('Sending "%s", attempt %d…', message, attempt)

        try:
            self.socket.send(message.encode())
            response = self.read()

            message.validate_response(response)

            data = Message.decode_data(response)
            LOGGER.info('Received message data is "%s"', data)

            return data

        except socket.timeout:
            if attempt >= self.retries:
                raise
            LOGGER.warning('Timeout occured, retrying…')
            return self.send_message(message, attempt + 1)
