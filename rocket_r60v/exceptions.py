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


class MessageLengthError(RocketError):
    '''
    Exception which is thrown when the message length is invalid.
    '''


class ValidationError(RocketError):
    '''
    Exception which is thrown when a message couldn't be validated successfully.
    '''


class SettingValueError(RocketError):
    '''
    Exception which is thrown when an invalid value is specified for a setting.
    '''
