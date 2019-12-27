'''
Coffee cycles settings.
'''

__all__ = (
    'TotalCoffeeCount',
)

from .base import ReadOnlySetting


class TotalCoffeeCount(ReadOnlySetting):
    '''
    The coffee cycles.
    '''
    address = 77
