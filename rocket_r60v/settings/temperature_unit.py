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
    address = 0

    choices = (
        'Celsius',
        'Fahrenheit',
    )
