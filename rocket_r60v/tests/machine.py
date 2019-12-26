#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the Rocket machine module.
'''

from unittest import TestCase, main
from unittest.mock import patch

from rocket_r60v.machine import Machine
from rocket_r60v.exceptions import RocketConnectionError


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
    def test_socket_missing_hello(self, socket_mock_function):
        '''
        Test if ``RocketConnectionError`` is raised when socket connects but
        machine doesn't respond with ``*HELLO*``.
        '''
        machine = Machine()
        with self.assertRaises(RocketConnectionError):
            machine.connect()

    @patch('rocket_r60v.api.socket.create_connection')
    def test_socket_connect(self, socket_mock_function):
        '''
        Test the socket connection.
        '''
        socket_mock_function.return_value.recv.return_value = b'*HELLO*'
        Machine().connect()
        socket_mock_function.assert_called_with(('192.168.1.1', 1774), 3.0)


if __name__ == '__main__':
    main()
