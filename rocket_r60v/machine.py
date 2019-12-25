'''
Rocket machine module.
'''

import logging
import socket
from inspect import getmembers, isclass
from re import sub

from . import settings
from .exceptions import RocketConnectionError

LOGGER = logging.getLogger(__name__)


class Machine:
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
        self.settings = dict(self.init_settings())
        self.socket  = None

    def __del__(self):
        '''
        Destructor.
        '''
        self.disconnect()

    def __getattr__(self, name):
        '''
        Let the user access the machine's settings via instance properties.
        '''
        if name == 'settings':
            return {}

        if name in self.settings:
            LOGGER.debug('Reading "%s" via instance property', name)
            return self.settings[name].get()

        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        '''
        Let the user set the machine's settings via instance properties.
        '''
        if name in self.settings:
            LOGGER.debug('Setting "%s" via instance property to "%s"', name, value)
            return self.settings[name].set(value)
        return super().__setattr__(name, value)

    def init_settings(self):
        '''
        Initialise all properties / settings of the machine.

        The settings will automatically be discovered by looking at all classes
        in the settings package. The settings are then available via instance
        properties of this class.
        '''
        for name, member in getmembers(settings):
            if not isclass(member):
                continue
            setting = member(self)
            name    = sub('([a-z])([A-Z])', r'\1_\2', name).lower()
            yield name, setting

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
        return self.socket.recv(self.buffer_size).decode()

    def send(self, data, attempt=1):
        '''
        Send data (i.e. raw message) to the machine and wait for response.

        :param str data: The data
        :param int count: The attempt counter

        :return: The received data
        :rtype: str
        '''
        LOGGER.debug('Sending "%s", attempt %d…', data, attempt)
        try:
            self.socket.send(data.encode())
            return self.read()
        except socket.timeout:
            if attempt >= self.retries:
                raise
            LOGGER.warning('Timeout occured, retrying…')
            return self.send(data, attempt + 1)
