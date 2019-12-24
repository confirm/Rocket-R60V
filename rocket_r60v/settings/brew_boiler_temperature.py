'''
Brew boiler temperature setting.
'''

__all__ = (
    'BrewBoilerTemperature',
)

from .base import RangeSetting


class BrewBoilerTemperature(RangeSetting):
    '''
    The temperature of the brew boiler.
    '''
    offset = 2

    range = (80, 110)