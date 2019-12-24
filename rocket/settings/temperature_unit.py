'''
Temperature unit setting.
'''

__all__ = (
    'TemperatureUnit',
)

from .base import ChoiceSetting


class TemperatureUnit(ChoiceSetting):
    '''
    The temperature unit in Celsius or Fahrenheit.
    '''
    offset = 0

    choices = (
        'Celsius',
        'Fahrenheit',
    )
