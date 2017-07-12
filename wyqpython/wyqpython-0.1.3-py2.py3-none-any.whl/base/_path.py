'''
Created on 2017年7月12日

@author: WYQ
'''

class Path:
    '''
    Path functions
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def get_desktop():
        '''
        Get Desktop path
        '''
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]