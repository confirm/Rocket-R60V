'''
Service boiler setting.
'''

__all__ = (
    'ServiceBoiler',
)

from .base import ChoiceSetting


class ServiceBoiler(ChoiceSetting):
    '''
    The state of the service boiler.
    '''
    offset = 73

    choices = (
        'off',
        'on',
    )
