'''
Created on Mar 6, 2014

@author: mgshow
'''

class FileReader(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__file=None
        self.__error=""
        self.__line=None
        self.__nextLine=None
        self.__error=""
    
    def open(self, path, encoding=None):
        
        try:  
            self.error=""
            self.__file=open(path, 'r')
            self.__nextLine=self.__file.readline()
            return True
        except Exception as err:
            self.__error=str(err)
            return False
     
    def geterror(self):
        return self.__error 
        
    def close(self):
        self.__file=None
        pass
    
    def nextline(self):
        if self.__file is None:
            return ''
        self.__line=self.__nextLine
        self.__nextLine=self.__file.readline()
        return self.__line
        
    def hasline(self):
        if self.__file is None:
            return False
        return  self.__nextLine != ""
        
        