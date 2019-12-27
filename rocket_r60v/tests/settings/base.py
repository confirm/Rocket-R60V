# pylint: disable=no-member
'''
Unit test cases for a Rocket settings module.
'''

import logging
from unittest import TestCase
from unittest.mock import patch

from rocket_r60v.machine import Machine
from rocket_r60v.exceptions import SettingValueError

logging.disable()


class TestSetting(TestCase):
    '''
    Base test case for a setting module.
    '''

    def _test(self, expected_request_message, response_message, expected_return_value, value=None):
        '''
        Test setting communication / messages.

        :param str expected_request_message: The expected request message
        :param str response_message: The response message which should be returned for testing
        :param str expected_return_value: The expected return value
        :param value: The value to set
        '''
        with patch('rocket_r60v.api.socket.create_connection') as mock_socket:
            machine  = Machine()
            instance = self.setting_class(machine)

            mock_socket.return_value.recv.return_value = b'*HELLO*'
            machine.connect()

            mock_socket.return_value.recv.return_value = response_message.encode()
            return_value = instance.get() if value is None else instance.set(value)

            mock_socket.return_value.send.assert_called_with(expected_request_message.encode())

            self.assertEqual(return_value, expected_return_value,
                             'Missmatch of return value via direct settings instance method')

            if value is None:
                return_value = getattr(machine, self.machine_property)
                self.assertEqual(return_value, expected_return_value,
                                 'Missmatch of return value via machine instance property')
            else:
                setattr(machine, self.machine_property, value)

            mock_socket.return_value.send.assert_called_with(expected_request_message.encode())

    def test_basic_validation(self):
        '''
        Test basic validation.
        '''
        instance = self.setting_class(None)

        if hasattr(instance, 'set'):
            with self.assertRaises(SettingValueError):
                instance.set(0)

            with self.assertRaises(SettingValueError):
                instance.set(None)

            with self.assertRaises(SettingValueError):
                instance.set('invalid-choice')
