'''
Created on Oct 1, 2012

@author: mgshow
'''

from xlem.utils import equalsnocase
import importlib
#import mysql.connector as MYSQL_CONNECTOR
#import xlem.drivers.MYSQL.MySQLConnection as MYSQL_CONN

class Connection(object):
    
    
    def __init__(self):
        pass
    
    def query(self, sqlQuery):
        pass
    
    def execute(self, sqlStatement):
        pass
    
    
    def nextrecord(self):
        return False
    
    def close(self):
        pass
    
    def getstring(self,columnName):
        return ""

class GenericDatabase(object):
    
    ERR_DATABASE_NOT_OPENED="Database not opened!"
    
    def __init__(self):
        self.XDBC=None
        self.connection=None
        self.error=""
        self.opened=False
    
    def geterror(self):
        return self.error
    
    def lasterror(self):
        return self.geterror()
    
    def resetError(self):
        self.error=""
    
    def open(self, relXDBC):
        self.XDBC=relXDBC
        self.resetError()
        try:
            self.connection=self.XDBC.getconnection()
            self.opened=True
        except Exception as ex:
            self.error=repr(ex)
        finally:
            return self.opened
    
    def query(self, sqlQuery):
        self.resetError()
        if not self.opened:
            self.error=self.ERR_DATABASE_NOT_OPENED
            return False
        try:
            self.connection.query(sqlQuery)
            return True
        except Exception as ex:
            self.error=repr(ex)
            return False
    
    def nextrecord(self):
        self.resetError()
        if not self.opened:
            self.error=self.ERR_DATABASE_NOT_OPENED
            return False
        try:
            return self.connection.nextrecord()
        except Exception as ex:
            self.error=repr(ex)
            return False
        
    def getstring(self, colNameOrIndex):
        self.resetError()
        if not self.opened:
            self.error=self.ERR_DATABASE_NOT_OPENED
            return ""
        try:
            return self.connection.getstring(colNameOrIndex)
        except Exception as ex:
            self.error=repr(ex)
            return ""
        
    def getinteger(self, colNameOrIndex):
        self.resetError()
        if not self.opened:
            self.error=self.ERR_DATABASE_NOT_OPENED
            return 0
        try:
            return self.connection.getinteger(colNameOrIndex)
        except Exception as ex:
            self.error=repr(ex)
            return 0
        
    def get(self, colNameOrIndex):
        self.resetError()
        if not self.opened:
            self.error=self.ERR_DATABASE_NOT_OPENED
            return None
        try:
            return self.connection.get(colNameOrIndex)
        except Exception as ex:
            self.error=repr(ex)
            return None
    
    def close(self):
        self.resetError()
        self.connection.close()
        self.XDBC=None
        self.opened=False
    
    pass

class XDBC(object):
    '''
    classdocs
    '''

    def __init__(self, _name, _type, _enabled, props ):
        '''
        Constructor
        '''
        self.name=_name
        self.type=_type
        self.enabled=_enabled
        self.props=props
        self.refClass=None
        
        if self.isMySql():
            module = importlib.import_module("xlem.drivers.MYSQL",'xlem')
            self.refClass = getattr(module, "MySQLConnection")
            #conn=self.getconnection()
            #conn.query("SELECT * FROM rnet.comm_frm_messages a order by fm_title limit 5")
            #while conn.nextrecord():
            #    print('Trovato:', conn.getstring('fm_title'), conn.getstring(0))
            #conn.close()
    
    def getconnection(self):
            obj =self.refClass()
            obj.open(self)
            return obj
            
    def isMySql(self):
        return equalsnocase(self.type, 'mysql')
         
    def getConnection(self):
        return self.getconnection()
    
    
    