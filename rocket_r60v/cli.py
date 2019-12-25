'''
CLI module.
'''

import argparse
import logging

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

        self.init_parser()
        self.init_parser_arguments()
        self.init_debug_parser()
        self.init_setting_parsers()

    def init_parser(self):
        '''
        Initialise the parser and subparser.
        '''
        self.parser = argparse.ArgumentParser(
            description='Remote control the Rocket R 60V.',
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
            help='verbose mode (-v for warning, -vv for info, -vvv for debug)',
        )

        self.parser.add_argument(
            '-f', '--logfile',
            nargs=1,
            dest='logfile',
            help='the filename of the logfile',
        )

    def init_debug_parser(self):
        '''
        Initialise the debug parser.
        '''
        parser = self.subparsers.add_parser(
            'debug',
            help='Manually send messages for debugging.',
        )

        parser.add_argument(
            'offset',
            type=int,
            help='Memory offset',
        )

        parser.add_argument(
            'length',
            type=int,
            nargs='?',
            default=1,
            help='Data length',
        )

        parser.add_argument(
            '-d', '--data',
            type=str,
            nargs='?',
            default='',
            help='The data to write'
        )

    def init_setting_parsers(self):
        '''
        Make the machine settings available to the parser.
        '''
        for argument, setting in self.machine.settings.items():
            setting_parser = self.subparsers.add_parser(
                argument,
                help=setting.__class__.__doc__.strip()
            )

            kwargs = {'nargs': '?'}
            if hasattr(setting, 'choices'):
                kwargs['choices'] = setting.choices

            if hasattr(setting, 'set_cli_value'):
                setting_parser.add_argument('value', **kwargs)

    def execute(self):
        '''
        Parse the CLI arguments and execute the actions.
        '''
        args = self.args = self.parser.parse_args()

        logging_config = {
            'format': '%(asctime)s - %(module)s - [%(levelname)s]: %(message)s',
            'level': 40 - (args.verbose * 10),
            'filename': args.logfile
        }
        logging.basicConfig(**logging_config)

        self.machine.connect()

        if args.action == 'debug':
            return self.execute_debug_action()
        else:
            return self.execute_machine_action()

    def execute_debug_action(self):
        '''
        Execute debug action.
        '''
        args = self.args
        data = args.data

        message = Message(
            command='w' if data else 'r',
            offset=args.offset,
            length=args.length,
            data=data,
            convert_int=False,
        )

        return self.machine.send_message(message)

    def execute_machine_action(self):
        '''
        Execute machine action.
        '''
        args    = self.args
        machine = self.machine

        if hasattr(args, 'value') and args.value:
            setattr(machine, args.action, args.value)
        else:
            return getattr(machine, args.action)
