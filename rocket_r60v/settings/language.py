'''
Language setting.
'''

__all__ = (
    'Language',
)

from .base import ChoiceSetting


class Language(ChoiceSetting):
    '''
    The language of the machine.
    '''
    address = 1

    choices = (
        'English',
        'German',
        'French',
        'Italian',
    )
