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

import sys
import xlem.runtime.XLemServer as XLEM_SERVER

usage='''
USAGE: RunServer <path> [additional parameters]
    
 additional parameters:
     
    -c <config-file>         {Default : <path>/xlews.xml}
    -ln <language>           {Overrides server language}
    -o <output-log-file>     {Creates server console to the specified path}
    -p <port-number>         {Overrides port number [0 <=> 65535]}
    -w <work-directory>      {Overrides <work-directory> for this server}
    
      
'''


if __name__ == '__main__':
    
    if len(sys.argv)<2:
        print("INVALID ARGUMENTS : please specify <path>")
        print(usage)
        sys.exit(0)
    
    args=sys.argv
    
    xlemServer= XLEM_SERVER.XLemServer()
    xlemServer.start_server(args[1],args)
    