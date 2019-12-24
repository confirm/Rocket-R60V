#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the Rocket machine module.
'''

from unittest import TestCase, main
from unittest.mock import patch

from rocket.machine import Machine
from rocket.exceptions import RocketConnectionError


class TestMachine(TestCase):
    '''
    Test rocket.machine.Machine class and its methods.
    '''

    @patch('rocket.machine.Machine.connect')
    def test_auto_connect(self, connect_mock_method):
        '''
        Make sure the ``connect`` method is called.
        '''
        Machine()
        connect_mock_method.assert_called()

    def test_localhost_connection_refused(self):
        '''
        Make sure ``ConnectionRefusedError`` is raised.
        '''
        with self.assertRaises(ConnectionRefusedError):
            Machine(address='127.0.0.1')

    def test_unreachable_address(self):
        '''
        Make sure ``RocketConnectionError`` is raised when address is not reachable.
        '''
        with self.assertRaises(RocketConnectionError):
            Machine(address='127.1.0.1')

    @patch('rocket.machine.socket.create_connection')
    def test_socket_missing_hello(self, socket_mock_function):
        '''
        Test if ``RocketConnectionError`` is raised when socket connects but
        machine doesn't respond with ``*HELLO*``.
        '''
        with self.assertRaises(RocketConnectionError):
            Machine()

    @patch('rocket.machine.socket.create_connection')
    def test_socket_connect(self, socket_mock_function):
        '''
        Test the socket connection.
        '''
        socket_mock_function.return_value.recv.return_value = b'*HELLO*'
        Machine()
        socket_mock_function.assert_called_with(('192.168.1.1', 1774), 3.0)


if __name__ == '__main__':
    main()
