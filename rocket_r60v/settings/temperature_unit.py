'''
Temperature unit setting.
'''

__all__ = (
    'TemperatureUnit',
)

from .base import ChoiceSetting


class TemperatureUnit(ChoiceSetting):
    '''
    The temperature unit.
    '''
    address = 0x00

    choices = (
        'Celsius',
        'Fahrenheit',
    )
