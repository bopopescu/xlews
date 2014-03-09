'''
Created on Mar 6, 2014

@author: mgshow

Copyright 2012-2014 XLEM by Lemansys S.r.l. - ITALY

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

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
        
        