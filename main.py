#!/usr/bin/env python
# pylint: disable=invalid-name
'''
CLI script for the Rocket R 60V.
'''

import argparse
import logging
import sys

from rocket.machine import Machine
from rocket.exceptions import RocketError

if __name__ == '__main__':

    parser    = argparse.ArgumentParser(description='Remote control the Rocket R 60V.')
    subparser = parser.add_subparsers(dest='setting')

    parser.add_argument(
        '-v',
        action='store_true',
        dest='verbose',
        help='Verbose mode',
    )

    machine = Machine()

    for argument, setting in machine.settings.items():
        setting_parser = subparser.add_parser(argument, help=setting.__class__.__doc__.strip())

        kwargs = {'nargs': '?'}
        if hasattr(setting, 'choices'):
            kwargs['choices'] = setting.choices

        setting_parser.add_argument('value', **kwargs)

    args = parser.parse_args()

    logging.basicConfig(
        filename='rocket.log',
        level=logging.INFO,
        format='%(asctime)s - %(module)s - [%(levelname)s]: %(message)s'
    )
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        machine.connect()

        if args.value:
            setattr(machine, args.setting, args.value)
        else:
            data = getattr(machine, args.setting)
            sys.stdout.write(f'{data}\n')

    except RocketError as ex:
        sys.stderr.write(f'{ex}\n')
        sys.exit(1)
