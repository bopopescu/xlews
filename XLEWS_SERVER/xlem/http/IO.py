'''
Created on May 20, 2012

@author: mgshow
'''
from datetime import datetime as __DATETIME__
import urllib.request as REQUEST
from xlem.utils import isblank,generateKEY,trim,tointeger
from threading import Lock as Lock


#from encodings.utf_8 import decode

class XLemHttpResponse(object):
    
    def __init__(self, requestHandler):
        '''
        Constructor
        '''
        self.content_type="text/html"
        self.charset_encoding="utf-8"
        self.request_handler=requestHandler
          
    def addheader(self, header_name, header_message):
        pass
    
    def write_String(self, s):
        self.request_handler.write_String(s)
        
    def write_Header(self, s, name):
        self.request_handler.write_Header(s, name)  
        
    def sendredirect(self, newurl):
        '''
        pw.write("HTTP/1.1 303 See other\r\n");
    pw.write("Location: "+url+"\r\n");
    pw.write(this.splitparameters());
    pw.write("Connection: close\r\n");
    pw.write("\r\n");
    pw.flush();}
        '''
        self.write_String("HTTP/1.1 303 See other\n")
        self.write_String("Location: "+newurl+"\n")
        self.write_String("Connection: close\n")
        self.write_String("\n")
        
    
    def getcharsetencoding(self):
        return self.charset_encoding
    
    def getCharsetEncoding(self):
        return self.getcharsetencoding()
    
    def setcharsetencoding(self, enc):
        self.charset_encoding=enc
        
    def setCharsetEncoding(self, enc):
        self.setcharsetencoding(enc)
        
    def setcontenttype(self, s):
        self.content_type=s
        
    def setContentType(self, s):
        self.setcontenttype(s)  
        
    def getcontenttype(self):
        return self.content_type
        
    def getContentType(self):
        return self.getcontenttype()
    
  

class XLemQueryString(object):
    
    def __init__(self, query, encoding):
        self.query=query
        self.encoding=encoding
        self.parameters={}
        
        if query is None:
                self.query=""
        
        x=self.query.split('&')
    
       
        for v in x:
            y=v.split('=')
            if len(y)>1:
                if(self.parameters.get(y[0]))==None:
                    self.parameters[REQUEST.unquote(y[0],'utf-8').replace('+',' ')]=[REQUEST.unquote(y[1],'utf-8').replace('+',' ')]
                else:
                    self.parameters[REQUEST.unquote(y[0],'utf-8').replace('+',' ')].append(REQUEST.unquote(y[1],'utf-8').replace('+',' '))
                             
        pass
    
    
    def toString(self):
        return self.query
    
    def tostringarray(self,attr):
        if attr is None:
            return None
        
        s=self.parameters.get(attr)
        
        return s
    
    def tointeger(self, attr):
        return tointeger(self.tostring(attr))
    
    def tostring(self, attr):
        if attr is None:
            return ""

        s=self.parameters.get(attr)
        
        if s is None:
            return ""
                
        return s[0]
            
        
class XLemHttpRequest(object):
    
    def __init__(self, requestHandler):
        '''
        Constructor
        '''
        self.__attributes={}
        self.parameters={}
        self.__request_handler=requestHandler
        self.querystring=XLemQueryString(requestHandler.getQueryString(),"utf-8")
    
    def hasheader(self, headerName):
        return self.getheader(headerName) is not None
    
    def getheader(self, headerName):
        x=self.__request_handler.headers.get(headerName)
        if x is None:
            return ""
        return x
    
    def getServerName(self):
        return self.getheader("host").split(":")[0]
    
    def getservername(self):
        return self.getServerName()
    
    def getfrontendport(self):
        x=self.getheader("host").split(":")
        if len(x>1):
            return int(x[1])
        return self.getServerPort()
    
    def getserverport(self):
        return self.getServerPort()
    
    def getServerPort(self):
        return self.__request_handler.get_port()
    
    def getHeader(self, headerName):
        return self.getheader(headerName)
    
    def getheaders(self):
        
        lst=[]
        for header in self.__request_handler.headers:
            lst.append(header)
        return lst    
    
    def getapplication(self):
        return self.__request_handler.get_application()
    
    def getsessioncookieid(self):
        for x in self.getheader('cookie').split(';'):
            y=trim(x).split("=")
            if len(y)>1:
                if y[0]=='xlemsessionid':
                    return y[1]
            pass
        return ""
             
    def getsession(self, createOnFail=False):
        
        return self.getapplication().get_session(self,createOnFail)
    
    def getSession(self,createOnFail):
        return self.getsession(self,createOnFail)
        
    def parseRequest(self, strng, encoding):
        
        self.original_request=strng
        x=strng.split('&')
        for v in x:
            y=v.split('=')
            if len(y)>1:
                if(self.parameters.get(y[0]))==None:
                    self.parameters[REQUEST.unquote(y[0],encoding).replace('+',' ')]=[REQUEST.unquote(y[1],encoding).replace('+',' ')]
                else:
                    self.parameters[REQUEST.unquote(y[0],encoding).replace('+',' ')].append(REQUEST.unquote(y[1],encoding).replace('+',' '))
                             
        pass   
    
        
    def tostringarray(self,attr):
        if attr is None:
            return None
        
        s=self.parameters.get(attr)
        
        return s
        
    def tostring(self, attr):
        if attr is None:
            return ""

        s=self.parameters.get(attr)
        
        if s is None:
            return ""
                
        return s[0]
    
    def setattribute(self,attrName,attrValue):
        x={attrName:attrValue}
        lock = Lock()
        lock.acquire()
        try:
            self.__attributes.update(x)
        finally:
            lock.release()
        
    def getattribute(self,attrName):    
        return self.__attributes.get(attrName)
    
    def removeattribute(self, attrName):
        self.__attributes.pop(attrName)
        
    def getstring(self, attrName):
        x=self.getattribute(attrName)
        if x is None:
            return ""
        elif type(x) is str:
            return x
        return repr(x)    
    
    def getQueryString(self):
        return self.querystring

class XLemHttpSession(object):
    def __init__(self, application):
        self.__id=generateKEY()
        self.application=application
        self.creationDate=__DATETIME__.now()
        self.__attributes={}
        
    def getid(self):
        return self.__id   
    
    def getattribute(self, attrName):
        return self.__attributes.get(attrName) 
    
    def setattribute(self,attrName,attrValue):
        x={attrName:attrValue}
        
        lock = Lock()
        lock.acquire()
        try:
            self.__attributes.update(x)
        finally:
            lock.release()
        
class XLemApplication(object):
    
    #name="default" isDefault="true" path="/www" isAbsolute="false"
    
    def __init__(self, name, path, isAbsolutePath, isDefault, isEnabled, server):
        self.name=name
        self.path=path
        self.absolutePath=isAbsolutePath
        self.default=isDefault
        self.enabled=isEnabled
        self.__attributes={}
        self.__sessions={}
        self.server=server
        self.validate()
        self.__cache={}
    
    def XDBC(self, name):
        return self.server.XDBCs.get(name)
        
    def getcachedpage(self, pageKey):
        return self.__cache.get(pageKey)
    
    def setcachedpage(self, pageKey, byteCode):
        return self.__cache.update({pageKey:byteCode})
    
    def removecache(self):
        self.__cache.clear()
      
        
    
    def validate(self):
        if isblank(self.name):
            raise Exception("Missing app name in XML definition!")
    
    def getName(self):
        return self.name
    
    def isEnabled(self):
        return self.enabled
    
    def isAbsolutePath(self):
        return self.absolutePath
    
    def isDefault(self):
        return self.default
    
    def getRealPath(self):
        if self.isAbsolutePath():
            return self.path
        return self.server.SERVER_PATH+self.path
    
    def setattribute(self,attrName,attrValue):
        x={attrName:attrValue}
        
        lock = Lock()
        lock.acquire()
        try:
            self.__attributes.update(x)
        finally:
            lock.release()
        
    def getattribute(self,attrName):    
        return self.__attributes.get(attrName)
    
    def removeattribute(self, attrName):
        self.__attributes.pop(attrName)
    
    def get_session(self, request, createOnFail=False):
    
        return self.__get_sessionbyid(request.getsessioncookieid(), createOnFail)
    
    def __get_sessionbyid(self, session_id, createOnFail=False):
        
        
        s=self.__sessions.get(session_id)
        
        if s is None and createOnFail:
            s=XLemHttpSession(self)
            self.__sessions.update({s.getid():s})
        return s
        
    def getstring(self, attrName):
        x=self.getattribute(attrName)
        if x is None:
            return ""
        elif type(x) is str:
            return x
        return repr(x)  