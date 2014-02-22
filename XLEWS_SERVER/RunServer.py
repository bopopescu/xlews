'''
Created on Mar 5, 2012

@author: mgshow
'''

import sys
import xlem.runtime.XLemServer as XLEM_SERVER

'''
    USAGE RunServer <path> 
    
 additional parameters:
     
    -c <config-file>        {Default : <path>/xlews.xml}
    -p <port-number>        {Ovverides port number}
      
'''


if __name__ == '__main__':
    
    args=sys.argv
    
    xlemServer= XLEM_SERVER.XLemServer()
    xlemServer.start_server("/Users/mgshow/Documents/workspace/XLEM")
    