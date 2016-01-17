__author__ = 'pwwpcheng'

class DictToObj:
    '''
    Convert python dictionary to python object.
    '''
    def __init__(self, **entries):
        self.__dict__.update(entries)