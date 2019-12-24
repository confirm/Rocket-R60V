'''
Service boiler setting.
'''

__all__ = (
    'ServiceBoiler',
)

from .base import ChoiceSetting


class ServiceBoiler(ChoiceSetting):
    '''
    Is the service boiler on or off.
    '''
    offset = 73

    choices = (
        'off',
        'on',
    )
