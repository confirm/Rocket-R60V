'''
Standby setting.
'''

__all__ = (
    'Standby',
)

from .base import ChoiceSetting


class Standby(ChoiceSetting):
    '''
    The standby state of the machine.
    '''
    address = 74

    choices = (
        'off',
        'on',
    )
