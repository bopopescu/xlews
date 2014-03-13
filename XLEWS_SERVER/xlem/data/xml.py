'''
Created on Mar 9, 2014

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

import xml.sax
from threading import Thread

class SaxThread(Thread):
    
    def __init__(self, source):
        Thread.__init__(self)
        self.__source=source
        self.__handler=XLemContentHandler(self)
        self.__currTagName=""
        self.__isFirstTag=True
        
    def getCurrTagName(self):
        
        while self.__handler.isAlive() and self.__currTagName=="":
            self.__currTagName=self.__handler.getCurrTagName()
        return self.__currTagName
    
    def goToNext(self):
        self.__currTagName=""
        self.__handler.goToNext()
        #s=self.getCurrTagName()
        return self.__handler.isAlive()
        
        
    def close(self):
        self.__handler.close()
        if(self.isAlive()):
            self._stop()
        
    def run(self):
        print("SONO PARTITO ALLA GRANDE!")
        try:
            xml.sax.parse(self.__source, self.__handler, None)
        except Exception as err:
            print("ERRORE SAX", err)
            self.close()
        
        print("SAX THREAD FINITO!")
    pass

class XLemContentHandler(xml.sax.ContentHandler):
    def __init__(self, sourceThread:Thread):
        xml.sax.ContentHandler.__init__(self)
        self.__sourceThread=sourceThread
        #__currSTATUS='START_ELEMENT'
        self.__waitForNext=True
        self.__currTagName=""
        self.__isAlive=True
        
    def isAlive(self):
        return self.__isAlive
    
    def close(self):
        self.__isAlive=False
        
    def getCurrTagName(self):
        return self.__currTagName
    
    def goToNext(self):
        self.__currTagName=""
        #print("Sono sul tag:'",self.__currTagName,"' e passo al prossimo!")
        self.__waitForNext=False
        pass
    
    def startElement(self, name, attrs):
        self.__currTagName=""
        print("<<'" + name + "'>>")
        self.__currTagName=name
        self.__waitForNext = True
        while self.__isAlive and self.__waitForNext:
            pass
        self.__currTagName=""
        #self.__currTagName=""
        #if name == "address":
        #    print("\tattribute type='" + attrs.getValue("type") + "'")
 
    def endElement(self, name):
        print("<</'" + name + "'>>")
        self.__currTagName=""
        self.__currTagName="/"+name
        self.__waitForNext = True
        while self.__isAlive and self.__waitForNext:
            pass
        self.__currTagName=""
        
 
    def endDocument(self):
        print("HANDLER TERMINATO!")
        self.__isAlive=False
 
    def characters(self, content):
        print("characters '" + content + "'")
 

class XmlParser(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__thread=None
        self.__exception=None
        
    
    def geterror(self):
        if self.__exception is None:
            return ""
        return repr(self.__exception)
        
    def open(self, sourceFileName):
        
        try:
            source=open(sourceFileName)
            self.__thread=SaxThread(source)
            self.__thread.start()
            return True
        except Exception as ex:
            self.__exception=ex
            return False
        pass
    
    def close(self):
        
        self.__thread.close()
        print("THREAD CLOSED!")
        
        pass
    
    def currtagname(self):
        return self.__thread.getCurrTagName()
    
    def next(self):
        return self.__thread.goToNext()
    
    def istag(self,tagName):
        return self.currtagname()==tagName
    
    def isclosedtag(self,tagName):
        return self.istag("/"+tagName)
    
    def getnexttag(self):
        return self.__thread.goToNext()
        pass