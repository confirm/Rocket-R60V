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
        self.init_setting_parsers()
        self.init_debug_parsers()

    def init_parser(self):
        '''
        Initialise the parser and subparser.
        '''
        def get_help_formatter(prog):
            return argparse.HelpFormatter(prog, max_help_position=34, width=120)

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
            help='Verbose mode (-v for error, -vv for warning, -vvv for info, -vvvv for debug)',
        )

        self.parser.add_argument(
            '-f', '--logfile',
            nargs=1,
            dest='logfile',
            help='The filename of the logfile',
        )

    def init_debug_parsers(self):
        '''
        Initialise the debug parsers for manual reading & writing data.
        '''
        subparsers = self.subparsers

        parsers = (
            subparsers.add_parser(
                'read',
                help='Manually read memory data (debugging only).',
            ),
            subparsers.add_parser(
                'write',
                help='Manually write memory data (debugging only).',
            )
        )

        for parser in parsers:
            parser.add_argument(
                '-r', '--raw',
                action='store_true',
                help='Send raw data, do not convert to hex'
            )

            parser.add_argument(
                'offset',
                type=int,
                help='The memory offset',
            )

            parser.add_argument(
                'length',
                type=int,
                help='The data length',
            )

        parsers[1].add_argument(
            'data',
            help='The data'
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
            'level': 50 - args.verbose * 10,
            'filename': args.logfile
        }
        logging.basicConfig(**logging_config)

        self.machine.connect()

        if args.action in ('read', 'write'):
            return self.execute_debug_action()
        else:
            return self.execute_machine_action()

    def execute_debug_action(self):
        '''
        Execute debug action.
        '''
        args    = self.args
        action  = args.action
        convert = not args.raw

        if action == 'write':
            data = int(args.data) if convert else args.data
        else:
            data = ''

        message = Message(
            command=action[0],
            offset=args.offset,
            length=args.length,
            data=data,
            convert_int=convert,
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
