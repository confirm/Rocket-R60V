'''
Coffee cycles settings.
'''

__all__ = (
    'CoffeeCyclesTotal',
    'CoffeeCyclesSubtotal',
)

from .base import ReadOnlySetting


class CoffeeCyclesTotal(ReadOnlySetting):
    '''
    The coffee cycles.
    '''
    address = 75


class CoffeeCyclesSubtotal(ReadOnlySetting):
    '''
    The coffee cycles.
    '''
    address = 77
