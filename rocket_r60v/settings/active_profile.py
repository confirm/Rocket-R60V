'''
Active profile setting.
'''

__all__ = (
    'ActiveProfile',
)

from .base import ChoiceSetting


class ActiveProfile(ChoiceSetting):
    '''
    The active pressure profile.
    '''
    address = 71

    choices = (
        'A',
        'B',
        'C',
    )
