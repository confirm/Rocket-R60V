'''
Rocket exceptions module.
'''


class RocketError(Exception):
    '''
    Base exception for all Rocket errors.
    '''


class RocketConnectionError(RocketError):
    '''
    Exception which is thrown when a connection error occurs.
    '''


class ValidationError(RocketError):
    '''
    Exception which is thrown when a message couldn't be validated successfully.
    '''


class SettingValueError(RocketError):
    '''
    Exception which is thrown when an invalid value is specified for a setting.
    '''


class ReadOnlySettingError(RocketError):
    '''
    Error which is thrown when a read-only setting is trying to be written.
    '''