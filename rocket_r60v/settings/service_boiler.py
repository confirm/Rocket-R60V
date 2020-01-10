'''
Service boiler setting.
'''

__all__ = (
    'ServiceBoiler',
    'ServiceBoilerTemperature',
    'CurrentServiceBoilerTemperature',
)

from .base import ChoiceSetting, RangeSetting, ReadOnlySetting


class ServiceBoiler(ChoiceSetting):
    '''
    The state of the service boiler.
    '''
    address = 73

    choices = (
        'off',
        'on',
    )


class ServiceBoilerTemperature(RangeSetting):
    '''
    The desired temperature of the service boiler.
    '''
    address = 3

    range = (110, 126)


class CurrentServiceBoilerTemperature(ReadOnlySetting):
    '''
    The current temperature of the service boiler.
    '''
    address = 0xB001
