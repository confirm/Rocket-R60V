#!/usr/bin/env python
# pylint: disable=no-self-use,unused-argument
'''
Unit test cases for the Rocket message module.
'''

__all__ = (
    'TestMessage',
)

import logging
from unittest import TestCase, main

from rocket_r60v.message import Message
from rocket_r60v.exceptions import MessageLengthError

logging.disable()


class TestMessage(TestCase):
    '''
    Test rocket.machine.Machine class and its methods.
    '''

    def _test_message(self, expected, **kwargs):
        '''
        Test if created message instance matches the expected message format.
        '''
        message = Message(**kwargs)

        self.assertEqual(expected, str(message), 'Mismatch of string representation')
        self.assertEqual(expected, message.raw_message, 'Mismatch of raw message w/ checksum')
        self.assertEqual(expected[0:-2], message.message, 'Mismatch of message w/o checksum')
        self.assertEqual(expected[0:9], message.envelope, 'Mismatch of envelope')
        self.assertEqual(expected[0], message.command, 'Mismatch of command')
        self.assertEqual(int(expected[1:5], 16), message.address, 'Mismatch of address')
        self.assertEqual(int(expected[5:9], 16), message.length, 'Mismatch of length')
        self.assertEqual(expected[9:-2], message.data, 'Missmatch of data')
        self.assertEqual(expected.encode(), message.encode(), 'Missmatch of encoded message')

    def test_read_from_first_address(self):
        '''
        Read from the first address.
        '''
        self._test_message(
            expected='r00010001F4',
            command='r',
            address=1,
            length=1
        )

    def test_read_from_tenth_address(self):
        '''
        Read from the tenth address.
        '''
        self._test_message(
            expected='r000A000104',
            command='r',
            address=10,
            length=1
        )

    def test_write_list_data_to_first_address(self):
        '''
        Write to the first address with a list of data.
        '''
        self._test_message(
            expected='w00010001015A',
            command='w',
            address=1,
            length=1,
            data=[1]
        )

    def test_write_int_data_to_first_address(self):
        '''
        Write to the first address with an int as data.
        '''
        self._test_message(
            expected='w00010001015A',
            command='w',
            address=1,
            length=1,
            data=1
        )

    def test_write_str_data_to_first_address(self):
        '''
        Write to the first address with an int as data.
        '''
        self._test_message(
            expected='w00010001015A',
            command='w',
            address=1,
            length=1,
            data='1'
        )

    def test_write_list_data_to_sixth_address(self):
        '''
        Write to the sixth address with a list of data.
        '''
        self._test_message(
            expected='w003C0001106F',
            command='w',
            address=60,
            length=1,
            data=[16]
        )

    def test_write_int_data_to_sixth_address(self):
        '''
        Write to the sixth address with an int as data.
        '''
        self._test_message(
            expected='w003C0001106F',
            command='w',
            address=60,
            length=1,
            data=16
        )

    def test_write_str_data_to_sixth_address(self):
        '''
        Write to the sixth address with an int as data.
        '''
        self._test_message(
            expected='w003C0001106F',
            command='w',
            address=60,
            length=1,
            data='16'
        )

    def test_write_long_list_data(self):
        '''
        Write a long list of data with matching length.
        '''
        self._test_message(
            expected='w003C00040A141E28C7',
            command='w',
            address=60,
            length=4,
            data=[10, 20, 30, 40]
        )

    def test_write_too_short_list_data(self):
        '''
        Write a too short list of data.
        '''
        with self.assertRaises(MessageLengthError):
            Message(
                command='w',
                address=60,
                length=4,
                data=[10, 20, 30]
            )

    def test_write_too_long_list_data(self):
        '''
        Write a too long list of data.
        '''
        with self.assertRaises(MessageLengthError):
            Message(
                command='w',
                address=60,
                length=4,
                data=[10, 20, 30, 40, 50]
            )


if __name__ == '__main__':
    main()
