'''
WaterFeed setting.
'''

__all__ = (
    'WaterFeed',
)

from .base import ChoiceSetting


class WaterFeed(ChoiceSetting):
    '''
    The language of the machine.
    '''
    offset = 70

    choices = (
        'HardPlumbed',
        'Reservoir',
    )
