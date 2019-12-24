'''
Service boiler temperature setting.
'''

__all__ = (
    'ServiceBoilerTemperature',
)

from .base import RangeSetting


class ServiceBoilerTemperature(RangeSetting):
    '''
    The language of the machine.
    '''
    offset = 3

    range = (110, 126)
