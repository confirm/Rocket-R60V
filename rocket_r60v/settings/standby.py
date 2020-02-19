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
    address = 0x4A

    choices = (
        'off',
        'on',
    )
