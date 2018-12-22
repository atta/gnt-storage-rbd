'''
Created on 12.02.2013

@author: ajazdzewski
'''
import ConfigParser


class config(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)
        self.pool = self.config.get('rbd', 'pool')
        self.originpool = self.config.get('rbd', 'originpool')
