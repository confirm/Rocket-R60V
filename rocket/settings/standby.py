'''
Standby setting.
'''

__all__ = (
    'Standby',
)

from .base import ChoiceSetting


class Standby(ChoiceSetting):
    '''
    Is the machine in standby mode.
    '''
    offset = 74

    choices = (
        'off',
        'on',
    )
