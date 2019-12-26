'''
Brew boiler temperature setting.
'''

__all__ = (
    'BrewBoilerTemperature',
)

from .base import RangeSetting


class BrewBoilerTemperature(RangeSetting):
    '''
    The desired temperature of the brew boiler.
    '''
    address = 2

    range = (80, 110)
