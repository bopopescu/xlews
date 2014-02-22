'''
Created on Oct 2, 2012

@author: mgshow
'''
from xlem.runtime.RDBMS import Connection
import mysql.connector
from xlem.utils import tointeger,tostring, toboolean,lowercase

class MySQLConfig(object):
    
    
    def __init__(self, props):
    
        self.HOST = 'localhost'
        self.DATABASE = ''
        self.USER = ''
        self.PASSWORD = ''
        self.PORT = 3306
        self.CHARSET = 'utf8'
        self.UNICODE = True
        self.WARNINGS = True   
        
        self.loadConfig(props)
             
        pass
    
    def loadConfig(self,props):
        
        self.HOST=props.get('host')
        self.DATABASE=props.get('database')
        self.USER=props.get('user')
        self.PASSWORD=props.get('password')
        self.CHARSET=props.get('charset')
        self.PORT=tointeger(props.get('port'))
        self.UNICODE=toboolean(props.get('use_unicode'))
        self.WARNINGS=toboolean(props.get('get_warnings'))
        
    def getConfig(self):
        return {
            'host': self.HOST,
            'database': self.DATABASE,
            'user': self.USER,
            'password': self.PASSWORD,
            'charset': self.CHARSET,
            'use_unicode': self.UNICODE,
            'get_warnings': self.WARNINGS,
            'port': self.PORT,
            }

class MySQLConnection(Connection):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.db=None
        self.cursor=None
        self.xdbc=None
        self.rows=None
        self.columns={}
        
    def open(self, xdbc):
        
        #print(repr(xdbc.props))
        
        self.db = mysql.connector.Connect(**MySQLConfig(xdbc.props).getConfig())
        self.cursor=self.db.cursor()
        self.xdbc=xdbc
        pass
    
    
    def query(self, sqlQuery):
        
        self.cursor.execute(sqlQuery)
        i=0
        for cn in self.cursor.column_names:
            self.columns.update({lowercase(cn):i})
            i=i+1
        pass
    
    def getColPosition(self, colName):
        cn=lowercase(colName)
        v=self.columns.get(cn)
        if v is None:
            return -1
        return v
    
    def nextrecord(self):
        self.rows=self.cursor.fetchmany(1)
        if self.rows is None:
            return False
        if len(self.rows)==0:
            return False
        return True
    
    def get(self,colName):
        if type(colName) is int:
            return self.rows[0][colName]
        else:
            p=self.getColPosition(colName)
            if p<0:
                raise Exception('Invalid column name:'+repr(colName))
            return self.rows[0][p]
    
    def getinteger(self,colName):
        if type(colName) is int:
            return tointeger(self.rows[0][colName])
        else:
            p=self.getColPosition(colName)
            if p<0:
                raise Exception('Invalid column name:'+repr(colName))
            return tointeger(self.rows[0][p])
    
    def getstring(self,colName):
        if type(colName) is int:
            return tostring(self.rows[0][colName])
        else:
            p=self.getColPosition(colName)
            if p<0:
                raise Exception('Invalid column name:'+repr(colName))
            return tostring(self.rows[0][p])
    
    def close(self):
        try:
            self.cursor.close()
            
            #print('Db chiuso correttamente!')
        except Exception as ex:
            print("ERR:"+repr(ex))
    
        try:
            self.db.close()
        except Exception as ex:
            print("ERR:"+repr(ex))    
            