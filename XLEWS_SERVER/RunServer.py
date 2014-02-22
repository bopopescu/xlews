'''
Created on Mar 5, 2012

@author: mgshow
'''

import xlem.runtime.XLemServer as XLEM_SERVER

if __name__ == '__main__':
    
    xlemServer= XLEM_SERVER.XLemServer()
    xlemServer.start_server("/Users/mgshow/Documents/workspace/XLEM")
    