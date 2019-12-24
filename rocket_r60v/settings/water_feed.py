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
    offset = 70

    choices = (
        'HardPlumbed',
        'Reservoir',
    )
