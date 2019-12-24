'''
Brew boiler temperature setting.
'''

__all__ = (
    'BrewBoilerTemperature',
)

from .base import RangeSetting


class BrewBoilerTemperature(RangeSetting):
    '''
    The language of the machine.
    '''
    offset = 2

    range = (80, 110)
