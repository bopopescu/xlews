'''
Created on Mar 2, 2014

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

from datetime import datetime as __DATETIME__

class XLemDate(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__date=__DATETIME__.now().date()
        
    def setdate(self, year, month, day):
        self.__date=self.__date.replace(year,month,day)
        
    def settime(self, hours, minutes, seconds):
        y=self.__date.year
        m=self.__date.month
        d=self.__date.day
        self.__date=__DATETIME__(y,m,d,hours, minutes, seconds)

    def __repr__(self):
        return str(self.__date.strftime("%Y-%m-%d %H:%M:%S"))
    
    
    