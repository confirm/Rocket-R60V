'''
Display setting.
'''

__all__ = (
    'Display',
    'CurrentBrewTime',
)

from .base import ReadOnlySetting


class Display(ReadOnlySetting):
    '''
    The display content.
    '''
    address = 0xB007
    length  = 64

    def get(self):  # pylint: disable=arguments-differ
        '''
        Get the display content of the machine.

        :return: The display content
        :rtype: str
        '''
        response = super().get()
        string = ''

        for i in range(0, self.length):
            if i > 0 and i % 16 == 0:
                string += '\n'
            string += chr(response[i])

        return string


class CurrentBrewTime(Display):
    '''
    The current brew time, taken from the display.
    '''

    length = 16

    def get(self):  # pylint: disable=arguments-differ
        '''
        Get the current brew time.

        :return: The brew time
        :rtype: float or None
        '''
        response = super().get()
        if response.endswith('"'):
            return float(response[0:-1])
        return None
