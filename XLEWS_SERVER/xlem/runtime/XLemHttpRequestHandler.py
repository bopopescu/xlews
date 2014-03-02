'''
Created on Mar 5, 2012

@author: mgshow
'''
import http.server
import imp
import cgi,cgitb
from xlem.runtime.XLemParser import XLemParserEnvironment,XLemParserOptions
from xlem.runtime.XLemParser import XLemParser
from xlem.runtime.XLemException import XLemException
from xlem.http.IO import XLemHttpRequest,XLemHttpResponse
import time
from base64 import b64encode
from hashlib import sha1,md5
from struct import pack
from threading import Thread

class WebSocketInputThread(Thread):
    
    def setup(self, requestHandler, inst, request, messageInputHandler, messageOutputHandler):
        self.__rq=requestHandler
        #print('Attivato Thread di lettura',self.__rq)
        self.__messageInputHandler=messageInputHandler
        self.__messageOutputHandler=messageOutputHandler
        self.__inst=inst
        self.__request=request
    
    def shutdown(self):
        self.__live=False
    
    def isRunning(self):
        return self.__live
    
    def writeMessage(self,message):
        self.__rq.wfile.write(self.__messageOutputHandler(message))
        
    def run(self):
        self.__live=True
        __rq=self.__rq
        
        
        try:
            
            #opening...
            self.__inst.doXlemWebSocketOpen(self.__request, self, self.writeMessage)
            while self.__live:
                
                    m=self.__messageInputHandler(__rq.rfile)
                    if m is not None:
                        self.__inst.doXlemWebSocketGetMessage(self.__request, self.writeMessage, m)
                        #__rq.wfile.write(self.__messageOutputHandler(m))
                    else:
                        self.__live=False
        except Exception as errore:
                self.__live=False
                print('Error in Thread:',str(errore))
        try:
            #closing...
            self.__inst.doXlemWebSocketClose(self.__request, self, self.writeMessage)
        except:
            pass
        
        print('bye bye!')

def is_hybi00(headers):
    """
    Determine whether a given set of headers is HyBi-00-compliant.

    Hixie-76 and HyBi-00 use a pair of keys in the headers to handshake with
    servers.
    """

    return "Sec-WebSocket-Key1" in headers and "Sec-WebSocket-Key2" in headers

# Authentication for WS.

def complete_hybi00(headers, challenge):
    """
    Generate the response for a HyBi-00 challenge.
    """
    digits='0123456789'

    key1 = headers["Sec-WebSocket-Key1"]
    key2 = headers["Sec-WebSocket-Key2"]
    
    first = int("".join(i for i in key1 if i in digits)) / key1.count(" ")
    second = int("".join(i for i in key2 if i in digits)) / key2.count(" ")

    #print('first',first,'second',second)
   
    nonce = pack(">II8s", int(first), int(second), challenge)
    
    return md5(nonce).digest()

def get_MessageOld(rfile):
        b=rfile.read1(512)
        if b==b'':
            return None
        return b[1:len(b)-1].decode('utf-8')

def get_MessageNew(rfile):
        
        #tmp = self.__rq.rfile.read1(512)  
        
        tmp=rfile.read1(8192)
        
        #print('Body :',tmp)
      
        
        #data += tmp; 
        
        lunghezza=0
        shft=0
        
        if tmp[1]==0xfe:
            lunghezza=tmp[3]+(tmp[2]*256)
            #print('L U N G: ',lunghezza)
            shft=2
            pass
        else:
            lunghezza=tmp[1] ^ 0x80
            pass
        
        lunghezza=tmp[1] ^ 0x80
        
        if lunghezza==0:
            return None
        
        msk=tmp[2+shft:6+shft]
        mzg=tmp[6+shft:]
        
        if mzg==b'':
            return None
        
        return mask(mzg,msk)

def mask(buf, key):
    
    pippo=bytearray(len(buf))
    
    for i in range(0,len(buf)):
        pippo[i]=buf[i] ^ key[i % 4]
   
    return pippo.decode('utf-8')

def create_Message(msg,key):
    return b'\x81\x05'+b'abcde'

def create_MessageOld(msg):
    x=bytearray(msg.encode('utf-8'))
    return b'\x00'+x+b'\xff'

def convertToByte(l):
    if l<=15:
        return bytes.fromhex(hex(l).replace('x',''))
    else:
        return bytes.fromhex(hex(l).replace('0x',''))

def create_MessageNew(msg):
    x=bytearray(msg.encode('utf-8'))
    l=len(x)
    
    if l<=15:
        bL=bytes.fromhex(hex(l).replace('x',''))
    elif l<=125:
        bL=bytes.fromhex(hex(l).replace('0x',''))
    else:
        l1=int(l/256)
        l2=l-l1*256
        bL= b'\x7e'+convertToByte(l1)+convertToByte(l2)  
     
    return b'\x81'+bL+x

def create_Message2(msg, key):
    
    x=bytearray(msg.encode('utf-8'))
    for i in range(0,len(x)):
        x[i]=x[i] ^ key [i % 4]
        
    return b'\x81'+bytes.fromhex(hex(128+len(x)).replace('0x',''))+key+x
    

class XLemHttpRequestHandler(http.server.BaseHTTPRequestHandler):
   
    
    def do_POST(self):
        self.do_Service()
    
    def get_application(self):
        return self.__currApplication
    
    def set_application(self, application):
        self.__currApplication=application
    
    def do_GET(self):
        self.do_Service()
        
    def get_port(self):
        return self.XLEM_SERVER.get_port()
        
        
    def do_Service_WebSocket(self,inst, request,response):
        
        response_key=""
        y=""
       
        if is_hybi00(self.headers):
            tmp=self.rfile.read1(1024)
            tmp=complete_hybi00(self.headers,tmp)
            
            y=('''
HTTP/1.1 101 WebSocket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
Sec-WebSocket-Origin: __THE_ORIGIN__\r
Sec-WebSocket-Location: ws://__WEB_SOCKET_LOCATION__'''.strip().replace('__THE_ORIGIN__',self.headers.get('origin')).replace('__WEB_SOCKET_LOCATION__',self.headers.get('host')+self.path)+"\r\n\r\n")
            
            
            bb=y.encode('utf-8')+tmp
            self.wfile.write(bb)
            
            rThread=WebSocketInputThread()
            rThread.setup(self, inst, request, get_MessageOld, create_MessageOld)
            
        else:
            GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            key=self.headers.get('Sec-WebSocket-Key')
            t_key=sha1(key.encode('utf-8')+GUID.encode('utf-8'))
            response_key=b64encode(t_key.digest())
            
            y=('''
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: FINAL_KEY\r
WebSocket-Protocol: sample'''.strip()+"\r\n\r\n").replace('FINAL_KEY', response_key.decode('utf-8'))
            
            self.write_String(y)
            
            rThread=WebSocketInputThread()
            rThread.setup(self, inst, request, get_MessageNew, create_MessageNew)
            
        # Shared Thread Code for any protocol...    
        rThread.start()
        #time.sleep(1200)
        #while rThread.isRunning():
        inst.doXlemWebSocketMain(request, rThread, rThread.writeMessage)
        rThread.join()
        #    pass
        rThread.shutdown()
        
        self.connection.close()      
        
             
    def do_Service(self):


        _curr_app=None
              
        '''
        if self.headers.get('Upgrade') is not None:
            #print('Upgrade',self.headers.get('Upgrade'))
            self.do_Service_WebSocket()
            return
       '''
        
        try:
            for _hostname,_port in [self.headers.get('host').split(':')]:
                
                
                _virtual_host=self.XLEM_SERVER.getVirtualHost(_hostname)
                
                if _virtual_host:
                    
                    _curr_app=self.XLEM_SERVER.getApplication(_virtual_host.appName)
                    if _curr_app:
                       
                        pass
                
        except Exception as ex:
            print("ERRORE HOST",repr(ex))
            pass
        
        self.set_application(_curr_app)
        
        
        trueFile = self.getRealFile(_curr_app)
                
        if self.is_Dynamic(trueFile):
            self.do_SERVICE_DYNAMIC_FILE(trueFile)
        else:
            self.do_SERVICE_STATIC_FILE(trueFile)
    
    
    def getRealFile(self, application=None):
        if application:
            f=application.getRealPath()+ self.path
            pass
        else:
            f=self.XLEM_SERVER.SERVER_PATH + "/www" + self.path
        
        # remove querystring
        indx=f.find("?")
        if indx!=-1:
            f=f[0:indx]
        return f 
    
    def getQueryString(self):
        f=self.path
        indx=f.find("?")
        if indx!=-1:
            return f[indx+1:]
        else:
            return ""
        
    
    def is_Dynamic(self, trueFile):
        
        if trueFile.endswith(".xlem") or trueFile.endswith(".xlmh"):
        
            return True
        
        else:
            return False            
   
        
    def do_SERVICE_STATIC_FILE(self, trueFile):
        
        print("Serving static file...", trueFile)
       
        in_file = None
       
        try:
       
            in_file = open(trueFile, "rb")
            content = in_file.read()
            
            mimeTp = self.XLEM_SERVER.get_MimeType(trueFile)
            
            self.write_String('HTTP/1.1 200 OK\n')
            if not mimeTp is None:
                self.write_Header('Content-Type', mimeTp)
            self.write_Header('Content-Length', str(content.__len__()))
            self.write_Header('Connection', 'close')
            self.write_Header('Server-Name', self.XLEM_SERVER.SERVER_NAME)
            self.write_Header('Server-Version', self.XLEM_SERVER.SERVER_VERSION)
            self.write_String('\n')
            self.wfile.write(content)
            
        except (IOError, OSError) as err:            
            self.write_String('HTTP/1.1 404 Not Found\n\n')
            print (err)
        
        finally:
            if in_file is not None:
                in_file.close()
        
        
     
    def do_PARSE_LEM_FILE(self, env, opt, request, response):
        
        
        #print("Parsing lem file: "+env.sourceFile+ " at ["+env.sourcePath+"]") 
        parser=XLemParser(env,opt)
        
        pageKey=parser.do_GenerateClassName()
        
        # retrieve application
        application=request.getapplication()
        
        inst=application.getcachedpage(pageKey)
        
        if inst is not None:
            
            if inst.toBeReloaded():
                #call destroy
                inst=None
            
        
        if inst is None:
            
            parser.xlemParse()
            parser.xlemValidate()
            btCode=parser.xlem2py()
            
            #print("Ritornato",btCode)
            #print("Carico modulo!")
            try:
                modl=imp.load_compiled(parser.do_GenerateClassName(),btCode)
                #print("modulo caricato!")
                clss=modl.__getattribute__(parser.do_GenerateClassName())
                inst=clss()
                application.setcachedpage(pageKey,inst)
            except Exception as exLoad:
                print("COMPILE ERROR:",repr(exLoad))
                application.setcachedpage(pageKey,None)
        
        # filter for WebSocket
        
        if self.headers.get('Upgrade') is not None:
            #print('Upgrade',self.headers.get('Upgrade'))
            self.do_Service_WebSocket(inst,request,response)
            return
        
        inst.doXLemService(request,response)
        
        
    def do_SERVICE_DYNAMIC_FILE(self, trueFile):
        
        if trueFile.endswith(".xlmh"):
            self.write_String('HTTP/1.1 403 Forbidden\n\n')
            return
        
        xlem_file=None
        
        #print("Serving dynamic file...", trueFile)  
        
        #print("QueryString = "+self.getQueryString())
        
        # Creating request, response and query string...
        request=XLemHttpRequest(self)
        response=XLemHttpResponse(self)
        
        if self.command=="POST":
            #len_dati = int(self.get_header('content-length'))
            #dati = urllib.unquote_plus(self.rfile.read(len_dati))
            #print("request",repr(self.headers.keys()))
            len_dati = int(self.headers.get('content-length'))
            
            
            # check for post type...
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                print ("multipart!", repr(pdict))
                #query=cgi.parse_multipart(self.rfile, pdict)
                #cgitb.enable()
                #form = cgi.FieldStorage()
                print("len_dati",repr(len_dati))
                
                MAX_BUFFER_READ=8192
                
                to_be_read=len_dati
                
                tot_read=0
                
                #print("a=",repr(form))
                '''
                curr_status
                    =0 => before read 'boundary'
                    =1 => reading boundary
                    =2 => boundary readed
                    =10 => reading content-disposition
                    =19 => content-disposition readed
                    =20 => reading field value
                    =29 => field value readed
                    =30 => reading file content
                    =39 => file readed
                    =90 => ended
                '''
                curr_status=0
                
                t_line=""
                old_i=0
                form=b''
                currArr=b''
                
                while tot_read<len_dati:
                    to_be_read=len_dati-tot_read
                    if to_be_read>MAX_BUFFER_READ:
                        to_be_read=MAX_BUFFER_READ
                
                    currArr=self.rfile.read(to_be_read)
                    print("Bytes letti:",len(currArr),"/",len_dati)
                    
                    form=form+currArr
                    
                    # Searching for boundary
                    if curr_status==0:
                        
                        old_i=0
                        for i in range (0,len(form)-1):
                            if(form[i]==0x0d and form[i+1]==0x0a):
                                t_line=form[old_i:i]
                                print('brekko', t_line)
                                i=i+2
                                old_i=i
                                # boundary founded
                                curr_status=1
                                break
                        
                        print(form)
                        form=b''
                    
                    
                    tot_read=tot_read+len(currArr)
                    print("rimanenti:", len_dati-tot_read)
                   
                    pass 
                
                '''
                for i in range (0,len(form)-1):
                    if(form[i]==0x0d and form[i+1]==0x0a):
                        t_line=form[old_i:i]
                        print('brekko', t_line)
                        i=i+2
                        old_i=i
                        
                t_line=None
                form=None
                '''
                
            else:
                dati=self.rfile.read(len_dati).decode('utf-8')
                request.parseRequest(str(dati),'utf-8')
                
           
            print("Hoffinito!")
        
        try:
            
            xlem_file = open(trueFile, "rb")
            #content = xlem_file.read()
            
            env=XLemParserEnvironment()
            opts=XLemParserOptions()
            
            env.destPath=self.XLEM_SERVER.SERVER_WORK_DIRECTORY
            
            # Compose environment
            parts=trueFile.rpartition('/')
            env.sourceFile=parts[2]
            env.sourcePath=parts[0]+parts[1]
             
            # Define options
            
            # Parsing, converting and compiling file
            self.do_PARSE_LEM_FILE(env, opts, request, response)
           
       
        except (IOError, OSError) as err:            
            self.write_String('HTTP/1.1 404 Not Found\n\n')
            print (err)

        except (XLemException) as err:            
            self.write_String('HTTP/1.1 500 Server Error\n\n')
            print ("ERROR 500:", err)
        
        except (Exception) as err:
            self.write_String('HTTP/1.1 500 Server Error\n\n')
            print ("ERROR 500:", err)
        
        finally:
            if xlem_file is not None:
                xlem_file.close()
       
    
    def write_String(self, line):
        if isinstance(line,str):
            byts = line.encode('utf-8', 'strict') 
        else:
            byts=str(line).encode('utf_8', 'strict')
        self.wfile.write(byts)  
             
        
    def write_Header(self, headerName, headerValue):
        self.write_String(headerName + ': ' + headerValue + '\n')
