#!/usr/bin/env python
'''
CLI script for the Rocket R 60V.
'''

import logging
import sys

from rocket.machine import Machine
from rocket.exceptions import RocketError

logging.basicConfig(level=logging.DEBUG)


try:
    MACHINE = Machine()
    print(MACHINE.language)
except RocketError as ex:
    sys.stderr.write(f'{ex}\n')
    sys.exit(1)
