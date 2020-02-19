'''
Water feed setting.
'''

__all__ = (
    'WaterFeed',
)

from .base import ChoiceSetting


class WaterFeed(ChoiceSetting):
    '''
    The source of the water feed.
    '''
    address = 0x46

    choices = (
        'HardPlumbed',
        'Reservoir',
    )
