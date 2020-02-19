'''
Brew boiler temperature setting.
'''

__all__ = (
    'BrewBoilerTemperature',
    'CurrentBrewBoilerTemperature',
)

from .base import RangeSetting, ReadOnlySetting


class BrewBoilerTemperature(RangeSetting):
    '''
    The desired temperature of the brew boiler.
    '''
    address = 0x02

    range = (80, 110)


class CurrentBrewBoilerTemperature(ReadOnlySetting):
    '''
    The current temperature of the brew boiler.
    '''
    address = 0xB000
