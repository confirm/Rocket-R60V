#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the Rocket machine module.
'''

__all__ = (
    'TestMachine',
)

import logging
from unittest import TestCase, main
from unittest.mock import patch

from rocket_r60v.machine import Machine
from rocket_r60v.exceptions import RocketConnectionError

logging.disable()


class TestMachine(TestCase):
    '''
    Test rocket.machine.Machine class and its methods.
    '''

    def test_localhost_connection_refused(self):
        '''
        Make sure ``ConnectionRefusedError`` is raised.
        '''
        machine = Machine(address='127.0.0.1')
        with self.assertRaises(ConnectionRefusedError):
            machine.connect()

    def test_unreachable_address(self):
        '''
        Make sure ``RocketConnectionError`` is raised when address is not reachable.
        '''
        machine = Machine(address='127.1.0.1')
        with self.assertRaises(RocketConnectionError):
            machine.connect()

    @patch('rocket_r60v.api.socket.create_connection')
    def test_socket_missing_hello(self, mock_socket):
        '''
        Test if ``RocketConnectionError`` is raised when socket connects but
        machine doesn't respond with ``*HELLO*``.
        '''
        machine = Machine()
        with self.assertRaises(RocketConnectionError):
            machine.connect()

    @patch('rocket_r60v.api.socket.create_connection')
    def test_socket_connect(self, mock_socket):
        '''
        Test the socket connection.
        '''
        mock_socket.return_value.recv.return_value = b'*HELLO*'
        Machine().connect()
        mock_socket.assert_called_with(('192.168.1.1', 1774), 3.0)


if __name__ == '__main__':
    main()
