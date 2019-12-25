'''
Rocket machine module.
'''

__all__ = (
    'Machine',
)

import logging
from inspect import getmembers, isclass
from re import sub

from .api import API
from . import settings

LOGGER = logging.getLogger(__name__)


class Machine(API):
    '''
    API class which can be used to connect and interact with the Rocket R60V.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Constructor.
        '''
        self.settings = dict(self.init_settings())
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        '''
        Let the user access the machine's settings via instance properties.
        '''
        if name == 'settings':
            return {}

        if name in self.settings:
            LOGGER.debug('Reading "%s" via instance property', name)
            return self.settings[name].get()

        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        '''
        Let the user set the machine's settings via instance properties.
        '''
        if name in self.settings:
            LOGGER.debug('Setting "%s" via instance property to "%s"', name, value)
            return self.settings[name].set(value)
        return super().__setattr__(name, value)

    def init_settings(self):
        '''
        Initialise all properties / settings of the machine.

        The settings will automatically be discovered by looking at all classes
        in the settings package. The settings are then available via instance
        properties of this class.
        '''
        for name, member in getmembers(settings):
            if not isclass(member):
                continue
            setting = member(self)
            name    = sub('([a-z])([A-Z])', r'\1_\2', name).lower()
            yield name, setting
