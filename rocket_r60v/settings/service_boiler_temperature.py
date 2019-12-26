'''
Service boiler temperature setting.
'''

__all__ = (
    'ServiceBoilerTemperature',
)

from .base import RangeSetting


class ServiceBoilerTemperature(RangeSetting):
    '''
    The desired temperature of the service boiler.
    '''
    address = 3

    range = (110, 126)
