'''
Created on Mar 5, 2012

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

import socketserver
import xlem.runtime.XLemHttpRequestHandler as REQUEST_HANDLER
import xml.etree.ElementTree as etree
from xlem.utils import toboolean
from xlem.http.IO import XLemApplication
from xlem.runtime.RDBMS import XDBC

class XLemVirtualHost(object):


    def __init__(self, server, name, appName, isEnabled,home):
        self.name=name
        self.server=server
        self.appName=appName
        self.enabled=isEnabled
        


class XLemServer(object):
    '''
    classdocs
    '''
    SERVER_PORT=-1
    SERVER_PATH=""
    SERVER_WORK_DIRECTORY=""
    MIME_TYPES={}
    SERVER_NAME='Lemansys XLEWS'
    SERVER_VERSION='1.0.0 Alpha'
    SERVER_CACHE={}
    
    def get_port(self):
        return self.SERVER_PORT
    
    def __init__(self):
        '''
        Constructor
        '''
        self.applications={}
        self.hosts={}
        self.defaultAppName= ""
        self.XDBCs={}
    
    def get_PageCached(self, fileName):
        return self.SERVER_CACHE.get(fileName)
    
    def set_PageCached(self, fileName, compiledByteCode):
        self.SERVER_CACHE.update(fileName, compiledByteCode)
        
        
    def start_server(self, serverPath, args=None):
        
        self.load_configuration(serverPath)
        self.load_mimetypes(serverPath)
        
        Handler = REQUEST_HANDLER.XLemHttpRequestHandler
        
        Handler.XLEM_SERVER=self
          
        realPort=int(self.SERVER_PORT)
        
        #Override parameters?
        if not args is None:
            
            for i in range(2,len(args)):
                print("PAR=",i,"=",repr(args[i]))
                if args[i]=='-p':
                    self.SERVER_PORT=args[i+1]
                    realPort=int(self.SERVER_PORT)
                    i=i+1
                elif args[i]=='-w':
                    self.SERVER_WORK_DIRECTORY=args[i+1]
            
            pass
        
        
        httpd = socketserver.ThreadingTCPServer(("", realPort), Handler)
        print(self.SERVER_NAME,self.SERVER_VERSION,"serving at port", self.SERVER_PORT, "WORK=",self.SERVER_WORK_DIRECTORY)
        httpd.serve_forever()
    
    def load_xdbc(self, xdbc):
        pN=""
        pV=""
        prps={}
        _name=xdbc.attrib.get('name')
        _type=xdbc.attrib.get('type')
        _enabled=toboolean(xdbc.get('enabled'))
        for chld in xdbc:
            if chld.tag=='xdbcprop':
                pN=chld.attrib.get('name')
                pV=chld.attrib.get('value')
                prps.update({pN:pV})
        return XDBC(_name, _type, _enabled, prps)
        
    def load_application(self, app):  
        #print("Reading application:", app.attrib.get('name'))
        t_name=app.attrib.get('name')
        t_path=app.attrib.get('path')
        t_absolutePath=toboolean(app.attrib.get('absolute'))
        t_default=toboolean(app.attrib.get('default'))
        t_enabled=toboolean(app.attrib.get('enabled'))
        
        
        t_app=XLemApplication(t_name, t_path, t_absolutePath, t_default, t_enabled, self)
        
        if self.applications.get(t_name) :
            raise Exception('Already existing application with name "'+t_name+'"')
        else:
            self.applications.update({t_name:t_app})
        
        if t_default:
            self.defaultAppName=t_name
            #print ("Default Application Name is now '"+self.defaultAppName+"'")
        
        #print("APP",t_name,t_path,t_absolutePath,"["+t_app.getRealPath()+"]",t_default, t_enabled)
        #print ("Application",t_name,"loaded on path", t_app.getRealPath())
        
        # Searching for xdbcs
        xdbcs=app.find('xdbcs')
        if xdbcs is not None:
            for xdbc in xdbcs:
                if xdbc.tag=='xdbc':
                    db=self.load_xdbc(xdbc)
                    self.XDBCs.update({db.name: db})
        pass
    
    def getApplication(self, appName):
        return self.applications.get(appName)
    
    
    def load_applications(self, root):
        applications = root.find('xlemApplications')
        for  app in applications:
            if app.tag=='xlemApp':
                self.load_application(app)
    
    def load_host(self, hst):  
        t_name=hst.attrib.get('name')
        t_application=hst.attrib.get('application')
        t_home=hst.attrib.get('home')
        t_enabled=toboolean(hst.attrib.get('enabled'))
        t_host=XLemVirtualHost(self, t_name, t_application, t_enabled, t_home)
        if self.hosts.get(t_name) :
            raise Exception('Already existing host with name "'+t_name+'"')
        else:
            self.hosts.update({t_name:t_host})
        #print ("Virtual Host",t_name,"loaded related to", t_host.appName+"application. Enabled=", t_host.enabled)
    
    def getVirtualHost(self, hostName):
        return self.hosts.get(hostName)
    
    def load_hosts(self, root):
        _hosts = root.find('xlemHosts')
        for  _host in _hosts:
            if _host.tag=='xlemHost':
                self.load_host(_host)
    
        
    def load_configuration(self, serverPath):
        tree = etree.parse(serverPath+"/cfg/xlem.xml")
        
        self.applications.clear()
        self.hosts.clear()
        
        root = tree.getroot()
        
        self.SERVER_PATH=serverPath
        self.SERVER_PORT=root.find('xlemTCP').text
        self.SERVER_WORK_DIRECTORY=root.find('xlemWorkDir').text.replace("$root",self.SERVER_PATH)
        self.load_applications(root)
        self.load_hosts(root)
        
        
    def load_mimetypes(self, serverPath): 
        tree = etree.parse(serverPath+"/cfg/mime-types.xml")
        root = tree.getroot()   
        for child in root:
            x={child.find('extension').text:child.find('mime-type').text}
            self.MIME_TYPES.update(x)
            
    
    def get_MimeType(self, fileName):
        indx=fileName.rfind('.')
        if indx<0:
            return None
        return self.MIME_TYPES.get(fileName[indx+1:])  
    
    def stop_server(self):
        
        self.stop_server()
        
        

        