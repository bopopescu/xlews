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

from datetime import datetime as __DATETIME__, time as __TIME__

class XLemDate(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__date=__DATETIME__.now().date()
        
    def adjust(self, years, months, days, hours, minutes, seconds ):
        
        
        dt=XLemDate()
        
        dt.__date=__DATETIME__.combine(self.__date.date(), self.__date.time())
        
        
        y=dt.getyear()+years
        m=dt.getmonth()+months
        d=dt.getday()+days
        hr=dt.gethour()+hours
        mn=dt.getminute()+minutes
        sc=dt.getsecond()+seconds
        
        # Fix years and months...
        while m<1 or m>12:
            
            if m>12:
                y=y+1
                m=m-12
            else:
                y=y-1
                m=m+12
            
            pass
        
        # Hours minutes and seconds...
        while sc<0 or sc>59:
            
            if sc>59:
                sc=sc-60
                mn=mn+1
            else:
                sc=sc+60    
                mn=mn-1
            pass
        
        # Minutes...
        while mn<0 or mn>59:           
            if mn>59:
                hr=hr+1
                mn=mn-60
            else:
                hr=hr-1
                mn=mn+60          
            pass
        # Hours
        while hr<0 or hr>23:    
            if hr>23:
                d=d+1
                hr=hr-24
            else:
                d=d-1
                hr=hr+24   
            pass 
        
        hwmn=self.__howmanydays(y,m)
        
        while d<1 or d>hwmn:
            
            if d>hwmn:
                m=m+1
                d=d-hwmn
                if m>12:
                    m=1
                    y=y+1
            else:
                m=m-1
                if m<1:
                    m=12
                    y=y-1
            
            pass
        
        
        dt.setdate(y, m, d)
        dt.settime(hr, mn, sc)
        
        return dt
        
        pass
    
    def __howmanydays(self,y,m):
        
        if m in (1,3,5,7,8,10,11):
            return 31
        elif m==2:
            if y-(y/4)*4==0 or y-(y/400)*400==0 and y-(y/100)*100>0:
                return 29
            else:
                return 28
            pass
        else:
            return 30
        pass
    
    def getweekday(self):
        return self.__date.weekday()
    
    def ismonday(self):
        return self.getweekday()==0
    
    def istuesday(self):
        return self.getweekday()==1
    
    def iswednesday(self):
        return self.getweekday()==2
    
    def isthursday(self):
        return self.getweekday()==3
    
    def isfriday(self):
        return self.getweekday()==4
    
    def issaturday(self):
        return self.getweekday()==5
    
    def issunday(self):
        return self.getweekday()==6
    
    def getyear(self):
        return self.__date.year
    
    def getmonth(self):
        return self.__date.month
    
    def getday(self):
        return self.__date.day
    
    def gethour(self):
        return self.__date.hour
    
    def getminute(self):
        return self.__date.minute
    
    def getsecond(self):
        return self.__date.second
        
    def setdate(self, year, month, day):
        self.__date=self.__date.replace(year,month,day)
        
    def settime(self, hour, minute, second):
        self.__date=__DATETIME__.combine(self.__date,__TIME__(hour,minute,second))

    def __repr__(self):
        return str(self.__date.strftime("%Y-%m-%d %H:%M:%S"))
    
    
    