'''
CLI module.
'''

import argparse
import logging
from time import sleep

from .message import Message


class CLI:
    '''
    CLI class which helps in creating and parsing the CLI arguments.
    '''

    def __init__(self, machine):
        '''
        Constructor.

        :param rocket_r60v.machine.Machine machine: The machine
        '''
        self.machine = machine
        self.args    = None

        self.init_parser()
        self.init_parser_arguments()
        self.init_setting_parsers()
        self.init_debug_parsers()

    def init_parser(self):
        '''
        Initialise the parser and subparser.
        '''
        def get_help_formatter(prog):
            return argparse.HelpFormatter(prog, max_help_position=40, width=120)

        self.parser = argparse.ArgumentParser(
            description='Remote control the Rocket R 60V.',
            formatter_class=get_help_formatter
        )

        self.subparsers = self.parser.add_subparsers(
            dest='action',
            required=True
        )

    def init_parser_arguments(self):
        '''
        Initialise the parser options for logging.
        '''
        self.parser.add_argument(
            '-v', '--verbose',
            action='count',
            default=0,
            dest='verbose',
            help='verbose mode (-v for error, -vv for warning, -vvv for info, -vvvv for debug)',
        )

        self.parser.add_argument(
            '-f', '--logfile',
            nargs=1,
            dest='logfile',
            help='the filename of the logfile',
        )

    def init_debug_parsers(self):
        '''
        Initialise the debug parsers for manual reading & writing data.
        '''
        self.subparsers.add_parser(
            'addresses',
            help='display all implemented memory addresses / settings (debugging)',
        )

        self.subparsers.add_parser(
            'monitor-brew-time',
            help='continously monitor brew time',
        )

        read_parser = self.subparsers.add_parser(
            'read',
            help='manually read memory data (debugging)',
        )

        write_parser = self.subparsers.add_parser(
            'write',
            help='manually write memory data (debugging)',
        )

        for parser in (read_parser, write_parser):
            parser.add_argument(
                'address',
                type=int,
                help='the memory address (unsigned 16-bit integer)',
            )

            parser.add_argument(
                'length',
                type=int,
                help='the data length (unsigned 16-bit integer)',
            )

        write_parser.add_argument(
            '-r', '--raw',
            action='store_true',
            help='send raw data, do not encode data to hex'
        )

        write_parser.add_argument(
            'data',
            help='the memory data (8-bit unsigned integers or hex value if raw)'
        )

    def init_setting_parsers(self):
        '''
        Make the machine settings available to the parser.
        '''
        for name, setting in self.machine.settings.items():

            doc = setting.__class__.__doc__.strip()
            doc = doc[0].lower() + doc[1:-1]

            setting_parser = self.subparsers.add_parser(
                name.replace('_', '-'),
                help=doc,
            )

            if hasattr(setting, 'set'):
                kwargs = {
                    'nargs': '?',
                    'choices': setting.choices if hasattr(setting, 'choices') else None
                }
                setting_parser.add_argument('value', **kwargs)

    def display_addresses(self):
        '''
        Display all configured memory addresses.

        :return: The memory addresses
        :rtype: str
        '''
        settings = sorted(self.machine.settings.items(), key=lambda x: x[1].address)
        addr = 'DEC HEX  LEN  SETTING\n'
        for name, setting in settings:
            addr += f'{setting.address:02d}  {setting.address:#04X} ({setting.length:02d}) {name}\n'
        return addr

    def execute(self):
        '''
        Parse the CLI arguments and execute the actions.

        :return: The response
        :rtype: str
        '''
        args = self.args = self.parser.parse_args()

        logging_config = {
            'format': '%(asctime)s - %(module)s - [%(levelname)s]: %(message)s',
            'level': 50 - args.verbose * 10,
            'filename': args.logfile
        }
        logging.basicConfig(**logging_config)

        if args.action == 'addresses':
            return self.display_addresses()

        self.machine.connect()

        if args.action in ('read', 'write'):
            return getattr(self, f'execute_{args.action}_action')()
        if args.action == 'monitor-brew-time':
            return self.monitor_brew_time()

        return self.execute_machine_action()

    def execute_read_action(self):
        '''
        Execute the read action.

        :return: The response
        :rtype: str
        '''
        message = Message(
            command='r',
            address=self.args.address,
            length=self.args.length,
        )

        return str(self.machine.send_message(message))

    def execute_write_action(self):
        '''
        Execute the write action.

        :return: The response
        :rtype: str
        '''
        message = Message(
            command='w',
            address=self.args.address,
            length=self.args.length,
            data=self.args.data,
            encode_data=(not self.args.raw)
        )

        return str(self.machine.send_message(message))

    def execute_machine_action(self):
        '''
        Execute machine action.

        :return: The response
        :rtype: str
        '''
        args    = self.args
        action  = args.action.replace('-', '_')
        machine = self.machine

        if hasattr(args, 'value') and args.value:
            setattr(machine, action, args.value)
            return 'OK'
        return str(getattr(machine, action))

    def monitor_brew_time(self):
        '''
        Continuously monitor the brew time.
        '''
        try:
            print('Starting brew time monitor. Press Ctrl-C to cancel…')
            while True:
                time = self.machine.current_brew_time
                if time is None:
                    sleep(1)
                    continue
                print(time)
        except KeyboardInterrupt:
            pass
