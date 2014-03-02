'''
Created on Nov 15, 2011

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
from xlem.runtime.XLemException import XLemException
from datetime import datetime as __DATETIME__
import py_compile
import re
import codecs
from xlem.utils import  *
from os.path import getmtime


class XLemParser(object):
    '''
    classdocs
    '''
    
    XLEM_PARSER_VERSION = "1.0.0"
    
    XLEM_VAR_NAME_REGEX = "[a-zA-Z]+" 
    
    XLEM_VAR_TYPE_DICT = {
                          
                          "string":"=''",
                          "integer": "=0",
                          "byte":"=0",
                          "double": "=0.0",
                          "boolean": "=False",
                          "float": "=0.0",
                          "long": "=0",
                          "date": "=XLemDate()",
                          
                          "buffer":"=[]",
                          "vector":"=XLemVector()",
                          "map":"=XLemMap()",
    
                          "genericdatabase": "=GenericDatabase()",
                         
                          #"xmlparser": "",
                          #"xmldocument": "",
                          #"xmlbuilder": "",
                          #"xmlview": "",
                          #"xsltransform" : ""
    
                          
                          }
    
    
    # "string|integer|double|float|string|boolean|date"
      
    XLEM_TAGS = [
                 "page","/page",
                 "content","/content",
                 "$TEXT","$REM","$EXPR",
                 "dim","set",
                 "if","/if","endif","else","elseif",
                 "for","forall","next","/for","/next","endfor","endforall","/forall",
                 "while","wend","/while","endwhile",
                 "try","/try","endtry","catch","/catch","endcatch","finally","endfinally",
                 "call","global","class",
                 "function","/function","endfunction","external",
                 "method","/method","endmethod","field","fields","/fields","endfields",
                 "model","/model","endmodel",
                 "switchout","/switchout","uselibrary","return",
                 "websocket:onmessage","/websocket:onmessage",
                 "websocket:open","/websocket:open", "websocket:close","/websocket:close",
                 "websocket","/websocket",
                 "ajax:action","/ajax:action",
                 "ui:activate","ui:calendar","ui:form","ui:panel","ui:section","ui:tab","ui:tabs",
                 "/ui:calendar","/ui:form","/ui:panel","/ui:tabs", "/ui:section", "/ui:tabs"
                 ]
    

    ''' Buffers/Lists '''
    runBfr=[]
    
   
    def __init__(self, parserEnvironment, parserOptions):
       
        self.xLemEnv = parserEnvironment   
        self.reset() 
        self.__useSession=False
        self.__createSessionOnFail=False
        self.__inContent=False
        
    def reset(self):
        self.xlemTokens = []
        self.xlemLibraries = []
    
    def existsTag(self, tagName=""):
        return tagName in self.XLEM_TAGS
    
    def addTag(self, tagName, tagContent):
        realTagName = tagName
        realTagContent = tagContent
        if realTagName == "":
            realTagName = "$TEXT"
        elif realTagName.startswith("="): 
            realTagName = "$EXPR"   
        elif realTagName.startswith("//"):
            realTagContent = realTagName[2:] + realTagContent 
            realTagName = "$REM" 
        
        #print ("newTag==> '" + realTagName + "' '" + realTagContent + "'")   
        self.xlemTokens.append(XLemTag(realTagName, realTagContent))
        
        
    def xlemParse(self):
        
        # Reset Buffer
        self.runBfr=[]
        self.funBfr=[]
        self.wsmBfr=[]
        self.wsbBfr=[]
        self.wsoBfr=[]
        self.wscBfr=[]
        self.outBfrName=""
         
        #f = open(self.xLemEnv.sourcePath + self.xLemEnv.sourceFile,"r")
        #f=codecs.getreader("utf-8")(open(self.xLemEnv.sourcePath + self.xLemEnv.sourceFile,"r"))
        
        fName=self.xLemEnv.sourcePath + self.xLemEnv.sourceFile
        
        f = codecs.open(fName,"r","utf-8")
       
        ST_TEXT_READING = 1
        ST_TAG_READING = 2
        ST_TAG_CONTENT_READING = 6
        
        
        self.xLemEnv.dependencies.update({fName:getmtime(fName)})
        
        
        ''' start parsing '''
        buffer=[]
        buffer.append(f.read())
        f.close()
        
        buffer.append("<@// End of file@>")
        
        s="".join(buffer)   
        
                 
        status = ST_TEXT_READING
        
        currTagName = "$TEXT"
        currTagContent = ""
        
        MAX_SOURCE_LENGTH = len(s)
            
        #s += "    "
        
        i = 0
        
        while i < MAX_SOURCE_LENGTH:
            ch = s[i]
            if ch == "<":
                if status == ST_TEXT_READING and s[i + 1] == '@':
                    self.addTag(currTagName, currTagContent)
                    currTagContent = ""
                    currTagName = ""
                    status = ST_TAG_READING
                    i += 1
                    
                else:
                    currTagContent += ch
            elif ch == "@":
                if status == ST_TAG_CONTENT_READING and s[i + 1] == '>':
                    status = ST_TEXT_READING
                    
                    self.addTag(currTagName, currTagContent)
                    
                    if currTagName=="external":
                        
                        XLEM_FILE_NAME=self.validateExternal(currTagName, currTagContent)
                        
                        subEnv=XLemParserEnvironment()
                        subEnv.sourcePath=self.xLemEnv.sourcePath
                        subEnv.sourceFile=XLEM_FILE_NAME+".xlmh"
                        subEnv.dependencies=self.xLemEnv.dependencies
                        sub=XLemParser(subEnv, None)
                        subTags=sub.xlemParse()  
                        for subTag in subTags:
                            self.addTag(subTag.getName(), subTag.getContent())   
                    
                    currTagContent = ""
                    currTagName = ""
                    i += 1
                elif  status == ST_TAG_READING and s[i + 1] == '>':
                    self.addTag(currTagName, currTagContent)
                    currTagContent = ""
                    currTagName = ""
                    status = ST_TEXT_READING
                    i += 1    
                else:
                    currTagContent += ch
            elif status == ST_TAG_READING:
                if ch == " ":
                    status = ST_TAG_CONTENT_READING 
                else:
                    currTagName += ch  
                    if currTagName=="=":
                        status=ST_TAG_CONTENT_READING
            elif status == ST_TAG_CONTENT_READING:
                currTagContent += ch                                 
            else:
                    currTagContent += ch
            i += 1
       
        return self.xlemTokens
    
    def xlemValidate(self):
        #print ("\r\n\r\nValidation processing...")
        tn=""
        for tag in self.xlemTokens:
            if not  self.existsTag(tag.getName()):
                raise XLemException("Invalid tag: "+tag.getName())
            #analize tags...
            tn=tag.getName()
            tag.writePass=False
            tag.writeThis=False
            if tn=='$TEXT':
                self.validateText(tag)
            elif tn=='$EXPR':
                self.validateExpr(tag)    
            elif tn == 'dim':
                self.validateVarDeclaration(tag)
                tag.writePass=False
            elif tn == 'field':
                self.validateFieldDeclaration(tag)
                tag.writePass=False
            elif tn=='set':
                self.validateSetVariable(tag)
            elif tn in ('if' ,'while', 'forall'):
                self.validateConditionalStatement(tag,0, False)
            elif tn in ('try'):
                self.validateConditionalStatement(tag,0, True)
            elif tn == 'for':
                self.validateForStatement(tag,0)
            elif tn=='else':
                tag.writePass=True
                self.validateConditionalStatement(tag, -1, True) 
            elif tn in('elseif','catch','finally'):
                self.validateConditionalStatement(tag, -1, False)  
                tag.writePass=True 
            elif tn in ('endif','wend', '/if' ,'/while', 'endwhile', 'wend','/for','endfor','next','endforall','/forall','/try','endtry'):   
                tag.writePass=True  
            #elif tn=='endif' or tn=='wend' or tn=='/if' or tn=='/while':
                self.validateCloseConditionalStatement(tag)               
            elif tn=='call':
                self.validateCall(tag)
            elif tn=='uselibrary':
                self.validateUseLibrary(tag)    
            elif tn=='content':
                self.validateContent(tag)    
            elif tn=='page':
                self.validatePage(tag)
            elif tn=='function':
                self.validateFunction(tag,0,False)      
            elif tn=='model':
                self.validateModel(tag,0,False) 
            elif tn=='fields':
                self.validateFields(tag,0,False)   
            elif tn == 'method':
                self.validateMethodStatement(tag,0)       
            elif tn=='return':
                self.validateReturn(tag)
            elif tn=='/function' or tn=='endfunction':
                self.validateCloseFunction(tag)  
            elif tn=='/model' or tn=='endmodel':
                self.validateCloseModel(tag)
            elif tn=='/fields' or tn=='endfields':
                self.validateCloseFields(tag)
            elif tn in ('/model', 'endmodel'):
                self.validateCloseModel(tag)
            elif tn in ('/method', 'endmethod'):
                self.validateCloseMethod(tag)      
            elif tn=='switchout':
                self.validateSwitchout(tag)  
            elif tn=='/switchout':
                self.validateCloseSwitchout(tag)
                
            elif tn.startswith("ui:") or tn.startswith("/ui:"):
                self.validateUI(tag)    
            '''
            elif tn=='websocket:onmessage':
                self.validateWebSocketOnMessage(tag,0,False)
            elif tn=='/websocket:onmessage':
                self.validateCloseWebSocketOnMessage(tag)      
            '''
        #print ("... validation successfully completed!")
    
    def validateUI(self,tag):
        
        nm=tag.getName()
        if nm=="ui:activate":
            
            bfr=[]
            bfr.append("response.write_String('\\n<link rel=\"stylesheet\" href=\"http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css\" />")
            bfr.append("\\n<script src=\"http://code.jquery.com/jquery-1.9.1.js\"></script>")
            bfr.append("\\n<script src=\"http://code.jquery.com/ui/1.10.3/jquery-ui.js\"></script>')")
            tag.setCompiled("".join(bfr))
            
        elif nm=="ui:calendar":
            
            pars=self.__retrievePars(tag)
            
            
            p_id=pars.get("id")
            
            bfr=[]
            bfr.append("response.write_String('\\n<script>$(function() {$( \"#"+p_id+"\" ).datepicker();});</script>")
            bfr.append("<input type=\"text\" id=\""+p_id+"\" />')")
            tag.setCompiled("".join(bfr))
            pass
        
        
        elif nm=="ui:form":
        
            bfr=[]
            bfr.append("response.write_String('\\n<form ")
            bfr.append(">')")
            tag.setCompiled("".join(bfr))
            pass
        
        elif nm=="/ui:form":
        
            tag.setCompiled("response.write_String('</form>')")
            pass
        
        
        elif nm=="ui:section":
            
            pars=self.__retrievePars(tag)
            
            p_id=self.__uiParseExpr(pars.get("id"))
            p_title=self.__uiParseExpr(pars.get("title"))
            
            bfr=[]
            bfr.append("response.write_String('\\n<script>$(function() {$( \"#"+p_id+"\" ).accordion({collapsible: true});});</script>")
            bfr.append("<div id=\""+p_id+"\" /><h3>"+p_title+"</h3><div>')")
            tag.setCompiled("".join(bfr))
            pass
        
        elif nm=="/ui:section":
            
            bfr=[]
            bfr.append("response.write_String('</div></div>')")
            tag.setCompiled("".join(bfr))
            pass
        
        pass
        
    
    def __uiParseExpr(self, s):
        
        if(isnull(s)):
            return ""
                       
        
        r=s.replace("${","'+tostring(")
        r=r.replace("}",")+'")
        return r
        
    def __retrievePars(self, tag):
        pars={}
        dim_re=re.compile("\s*(?P<COUPLE>(\w+\s*[=]\s*[\"][^\"]*[\"]))\s*",re.VERBOSE)
        dim_re2=re.compile("(?P<ATTR_NAME>\w+)\s*[=]\s*[\"](?P<ATTR_VALUE>[^\"]*)[\"]",re.VERBOSE)
        attrName=""
        attrValue=""
        for match in dim_re.finditer(tag.getContent()):
            for match2 in dim_re2.finditer(match.group("COUPLE")):
                attrName=match2.group('ATTR_NAME')
                attrValue=match2.group('ATTR_VALUE')
                pars.update({attrName:attrValue})
        return pars
    
    def validatePage(self, tag):
        
        pars=self.__retrievePars(tag)
        
        if toboolean(pars.get('session')):
            self.__useSession=True
            
        if toboolean(pars.get('createonfail')):
            self.__createSessionOnFail=True
            
    
    def validateContent(self, tag):
        
        self.__inContent=True
        
        pars=self.__retrievePars(tag)
        
        bfr=[]
        
        if pars.get("type") != None:
            
            bfr.append("response.setContentType('"+pars.get('type')+"')")
            pass
        
        if pars.get("encoding") != None:
            
            bfr.append("response.setCharsetEncoding('"+pars.get("encoding")+"')")
        
        
        bfr.append("__mimeTp = response.getContentType()")              
        bfr.append("response.write_String('HTTP/1.1 200 OK\\n')")
        bfr.append("if not __mimeTp is None:")
        bfr.append("    response.write_Header('Content-Type', __mimeTp+'; charset='+response.getCharsetEncoding())")
        bfr.append("response.write_Header('Connection', 'close')")
        bfr.append("response.write_Header('Server-Name', response.request_handler.XLEM_SERVER.SERVER_NAME)")
        bfr.append("response.write_Header('Server-Version', response.request_handler.XLEM_SERVER.SERVER_VERSION)")
        if self.__useSession:
            bfr.append("if not isnull(session):")
            bfr.append("    response.write_Header('Set-Cookie', ' xlemsessionid='+session.getid()+';path=/')")
            #add here other cookies
        bfr.append("response.write_String('\\n')")
        
        tag.setCompiled("\n            ".join(bfr))
        
     
    def validateText(self, tag):
        s=tag.getOriginalContent().strip()
        
        
        if s=="":
            return
        
        
        s=s.replace("\"","\\\"").replace("$_$"," ")
        
        
        if isblank(self.outBfrName):
                tag.setCompiled("response.write_String(\"\"\""+s.replace("\"\"\"","\\\"\\\"\\\"")+"\"\"\")")   
        else:
            tag.setCompiled(self.outBfrName+".append(\"\"\""+s.replace("\"\"\"","\\\"\\\"\\\"")+"\"\"\")")        
    
    def validateExpr(self, tag):
        if isblank(self.outBfrName):
            tag.setCompiled("response.write_String("+tag.getContent()+")") 
        else:
            tag.setCompiled(self.outBfrName+".append("+tag.getContent()+")")           
    
    
    def validateUseLibrary(self, tag):
        lb=trim(tag.getContent())
        
        if not lb.startswith('import') and not lb.startswith('from'):
            lb="import "+lb
        
        self.xlemLibraries.append(lb)
    
    def validateSwitchout(self, tag):
    
        if not isblank(self.outBfrName):
            raise XLemException("Already opened switchout into the page:'"+self.outBfrName+"' !!!")
        
    
        self.outBfrName=trim(tag.getContent())
        
        if isblank(self.outBfrName):
            raise XLemException('Missing buffer name into switchout statement!')
        
        pass
        
    def validateCloseSwitchout(self, tag):
        
        if isblank(self.outBfrName):
            raise XLemException('No switchout is currently opened!')
        
        self.outBfrName=""
    
    def validateExternal(self, tagName, tagContent):
        XLEM_FILE_NAME=""
        dim_re=re.compile("\s*src[\s]*[=][\s]*[\"](?P<XLEM_FILE_NAME>.+)[.]xlmh[\"]\s*",re.VERBOSE)  
        for match in dim_re.finditer(tagContent):
            XLEM_FILE_NAME=match.group("XLEM_FILE_NAME")
        
        if XLEM_FILE_NAME=="":
            raise XLemException("Invalid or missing module file name: <@external "+tagContent+"@>!")    
        return XLEM_FILE_NAME
    
    
    def validateVarDeclaration(self, tag):
        dim_re=re.compile("\s*(?P<XLEM_VAR_NAME>\w+)[\s]*as[\s]*(?P<XLEM_VAR_TYPE>\w+)\s*",re.VERBOSE)   
        for match in dim_re.finditer(tag.getContent()):
            XLEM_VAR_NAME=match.group("XLEM_VAR_NAME")
            XLEM_VAR_TYPE=match.group("XLEM_VAR_TYPE")
            if not self.XLEM_VAR_TYPE_DICT.__contains__(XLEM_VAR_TYPE):
                tag.setCompiled(XLEM_VAR_NAME+"="+XLEM_VAR_TYPE+"()")
                #raise XLemException("Unknow var type: '"+XLEM_VAR_TYPE+"'!")
            else:
                tag.setCompiled(XLEM_VAR_NAME+self.XLEM_VAR_TYPE_DICT.get(XLEM_VAR_TYPE))
        pass

    def validateFieldDeclaration(self, tag):
        dim_re=re.compile("\s*(?P<XLEM_VAR_NAME>\w+)[\s]*as[\s]*(?P<XLEM_VAR_TYPE>\w+)\s*",re.VERBOSE)   
        for match in dim_re.finditer(tag.getContent()):
            XLEM_VAR_NAME=match.group("XLEM_VAR_NAME")
            XLEM_VAR_TYPE=match.group("XLEM_VAR_TYPE")
            if not self.XLEM_VAR_TYPE_DICT.__contains__(XLEM_VAR_TYPE):
                tag.setCompiled("self.__addField__('"+XLEM_VAR_NAME+"',fieldValue="+XLEM_VAR_TYPE+"())")
                #raise XLemException("Unknow var type: '"+XLEM_VAR_TYPE+"'!")
            else:
                tag.setCompiled("self.__addField__('"+XLEM_VAR_NAME+"',fieldValue"+self.XLEM_VAR_TYPE_DICT.get(XLEM_VAR_TYPE)+")")
        pass

    
    def validateForStatement(self, tag, shiftPrev):
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        dim_re=re.compile("\s*(?P<XLEM_VAR_NAME>.+)[\s]*=[\s]*(?P<XLEM_VAR_FROM>.+)"+
                          "[\s]*to[\s]*(?P<XLEM_VAR_TO>.+)\s*(?P<XLEM_VAR_STEP>step)\s*(?P<XLEM_VAR_STEP_VALUE>.+)\s*",re.VERBOSE)   
        
        XLEM_VAR_NAME=""
        XLEM_VAR_TO=""
        XLEM_VAR_FROM=""
        for match in dim_re.finditer(tag.getContent()):
            XLEM_VAR_NAME=match.group("XLEM_VAR_NAME")
            XLEM_VAR_FROM=match.group("XLEM_VAR_FROM")
            XLEM_VAR_TO=match.group("XLEM_VAR_TO")  
            XLEM_VAR_STEP_VALUE=match.group("XLEM_VAR_STEP_VALUE")
            tag.setCompiled("for "+XLEM_VAR_NAME+" in range ("+XLEM_VAR_FROM+", ("+XLEM_VAR_TO+")+1, "+XLEM_VAR_STEP_VALUE+"):")
            return
        pass
        
        if XLEM_VAR_NAME=="" or XLEM_VAR_FROM=="" or XLEM_VAR_TO=="":
                dim_re=re.compile("\s*(?P<XLEM_VAR_NAME>.+)[\s]*=[\s]*(?P<XLEM_VAR_FROM>.+)"+
                          "[\s]*to[\s]*(?P<XLEM_VAR_TO>.+)\s*",re.VERBOSE)  
                for match in dim_re.finditer(tag.getContent()):
                    XLEM_VAR_NAME=match.group("XLEM_VAR_NAME")
                    XLEM_VAR_FROM=match.group("XLEM_VAR_FROM")
                    XLEM_VAR_TO=match.group("XLEM_VAR_TO")  
                    tag.setCompiled("for "+XLEM_VAR_NAME+" in range ("+XLEM_VAR_FROM+", ("+XLEM_VAR_TO+")+1):") 
                    return
        else:
            return
            
        if XLEM_VAR_NAME=="" or XLEM_VAR_FROM=="" or XLEM_VAR_TO=="":
                raise XLemException("Invalid for statement: "+repr(tag.getContent()))
    
    def validateSetVariable(self, tag):
        dim_re=re.compile("\s*(?P<XLEM_VAR_NAME>\w+)[\s]*[=][\s]*(?P<XLEM_VAR_VALUE>.+)\s*",re.VERBOSE)  
         
        for match in dim_re.finditer(tag.getContent()):
            XLEM_VAR_NAME=match.group("XLEM_VAR_NAME")
            XLEM_VAR_VALUE=match.group("XLEM_VAR_VALUE")
            tag.setCompiled(XLEM_VAR_NAME+"="+XLEM_VAR_VALUE)
        pass
    
    def validateCloseConditionalStatement(self, tag):
        tag.setShiftPrev(-1)
        tag.setShift(0)
        tag.setCompiled(' ')
    
    def validateFunction(self, tag, shiftPrev, emptyStatement):
        
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        
        tag.setCompiled("def "+ tag.getContent()+" :")
        
    def validateModel(self, tag, shiftPrev, emptyStatement):
        
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        
        tag.setCompiled("class "+ tag.getContent()+"(XLemModelBean) :")
        
    def validateFields(self, tag, shiftPrev, emptyStatement):
        
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        
        tag.setCompiled("def __initModelFields__(self) : ")
        
    def validateMethodStatement(self, tag, shiftPrev):
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        tag.writeThis=True
        
        dim_re=re.compile("\s*(?P<XLEM_METHOD_NAME>\w+)[\s]*[(]\s*(?P<XLEM_METHOD_ARGUMENTS>.*)\s*[)]\s*",re.VERBOSE)
        
        for match in dim_re.finditer(tag.getContent()):
            XLEM_METHOD_NAME=match.group("XLEM_METHOD_NAME")
            XLEM_METHOD_ARGUMENTS=match.group("XLEM_METHOD_ARGUMENTS")
            if isblank(XLEM_METHOD_ARGUMENTS):
                XLEM_METHOD_ARGUMENTS="self"
            else :
                XLEM_METHOD_ARGUMENTS="self, "+XLEM_METHOD_ARGUMENTS
            tag.setCompiled("def "+ XLEM_METHOD_NAME+" ( "+ XLEM_METHOD_ARGUMENTS+" ) :")  
            return
        pass
        
        raise XLemException("Invalid method definition: "+repr(tag.getContent()))
         
        
    def validateCloseFunction(self, tag):
        tag.writePass=True
        tag.setShiftPrev(-1)
        tag.setShift(0)
        tag.setCompiled(' ')
        
    def validateCloseModel(self, tag):
        tag.writePass=True
        tag.setShiftPrev(-1)
        tag.setShift(0)
        tag.setCompiled(' ')
        
    def validateCloseFields(self, tag):
        tag.writePass=True
        tag.setShiftPrev(-1)
        tag.setShift(0)
        tag.setCompiled(' ')
        
    def validateCloseMethod(self, tag):
        tag.writePass=True
        tag.setShiftPrev(-1)
        tag.setShift(0)
        tag.setCompiled(' ')
    
    def validateConditionalStatement(self, tag, shiftPrev, emptyStatement):
        
        tag.setShiftPrev(shiftPrev)
        tag.setShift(1)
        
        tn=tag.getName()
        if tn=="elseif":
            tn="elif"
        elif tn=="forall":
            tn="for"
        elif tn=="catch":
            tn="except"
        
        
        if emptyStatement:
            tag.setCompiled(tn+" :")
            return
        
        dim_re=re.compile("\s*(?P<XLEM_CALL_STATEMENT>.+)\s*",re.VERBOSE)   
        for match in dim_re.finditer(tag.getContent()):
            XLEM_CALL_STATEMENT=match.group("XLEM_CALL_STATEMENT")
            
            tag.setCompiled(tn+" "+XLEM_CALL_STATEMENT+" :")       
        pass
    
    def validateCall(self, tag):
        dim_re=re.compile("\s*(?P<XLEM_CALL_STATEMENT>.+)\s*",re.VERBOSE)   
        for match in dim_re.finditer(tag.getContent()):
            XLEM_CALL_STATEMENT=match.group("XLEM_CALL_STATEMENT")
            tag.setCompiled(XLEM_CALL_STATEMENT)
        pass
    
    def validateReturn(self, tag):
        dim_re=re.compile("\s*(?P<XLEM_CALL_STATEMENT>.+)\s*",re.VERBOSE)   
        for match in dim_re.finditer(tag.getContent()):
            XLEM_CALL_STATEMENT=match.group("XLEM_CALL_STATEMENT")
            tag.setCompiled("return " +XLEM_CALL_STATEMENT)
        pass
        
    def xlem2py(self):
        
        
        XLEM_PAGE_TEMPLATE="""
'''
        Created on $$CreatedDate$$
        XLEM page generator V.$$ParserVersion$$
        
'''
        
$$XLEMImport$$
      
class $$XLEMClassName$$(XLEM_PAGE):

        def doXlemWebSocketGetMessage(self,request, sendmessage, message):
            application=request.getapplication()
$$WSGetMessageBody$$
            pass
            
        def doXlemWebSocketOpen(self,request, __currentWebSocketThread, sendmessage):
            application=request.getapplication()
$$WSGetMessageOpen$$
            pass   
            
        def doXlemWebSocketClose(self,request, __currentWebSocketThread, sendmessage):
            application=request.getapplication()
$$WSGetMessageClose$$
            pass           
            
        def doXlemWebSocketMain(self,request, __currentWebSocketThread, sendmessage):
            application=request.getapplication()
            isrunning=__currentWebSocketThread.isRunning
$$WSBody$$
            pass
            
        def doXLemService(self,request,response):
            querystring=request.getQueryString()
            session=$$session_value$$
            application=request.getapplication()
            
        
$$RunBody$$


        def toBeReloaded(self):
            
            for d in self.__dependencies:
                try:
                    if self.__dependencies.get(d)!=getmtime(d):
                        #print('File',d,'has changed!' )
                        return True
                except Exception:
                    pass
                pass    
            
            return False
           
            
        def __init__(self):
            self.__dependencies={}
$$Dependencies$$
            #print("inizzio")
            pass    



        #$$MainScript$$        

# Custom Page functions...            
$$Functions$$


"""
        
        pyTxt=XLEM_PAGE_TEMPLATE
        pyTxt=pyTxt.replace("$$CreatedDate$$", __DATETIME__.now().isoformat())
        pyTxt=pyTxt.replace("$$ParserVersion$$", self.XLEM_PARSER_VERSION)
        pyTxt=pyTxt.replace("$$XLEMClassName$$",self.do_GenerateClassName())
        
        
        dpdcs=[]
        for dpdc in self.xLemEnv.dependencies:
            dpdcs.append("            self.__dependencies.update({'"+dpdc+"':"+str(self.xLemEnv.dependencies.get(dpdc))+"})")
        pyTxt=pyTxt.replace("$$Dependencies$$","\n".join(dpdcs))
        
        
        if self.__useSession:
            pyTxt=pyTxt.replace("$$session_value$$", "request.getsession("+repr(self.__createSessionOnFail)+")")
        else:
            pyTxt=pyTxt.replace("$$session_value$$","None")
        
        
        lbrs=[]
        lbrs.append("from xlem.http.XLemPage import  XLemPage as XLEM_PAGE")
        lbrs.append("from xlem.utils import  *")
        lbrs.append("from xlem.data import *")
        lbrs.append("from xlem.data.dateAndTime import *")
        lbrs.append("from xlem.data.collections import *")
        lbrs.append("from os.path import getmtime")
        lbrs.append("from xlem.runtime.RDBMS import GenericDatabase")
        for lb in self.xlemLibraries:
            lbrs.append(lb)
        
        pyTxt=pyTxt.replace("$$XLEMImport$$","\n".join(lbrs))
        
        shfts_run=3
        shfts_fun=0
        shfts_wsm=3
        shfts_wsb=3
        shfts_wso=3
        shfts_wsc=3
         
        
        currBfr=self.runBfr
        shfts=shfts_run
        retBfr=self.runBfr
        
        tNm=""
        
        for tag in self.xlemTokens:
            tNm=tag.getName()
            
            if(tag.getCompiled()!=""):
                if(tag.isWritePass()):
                    currBfr.append(self.generateLine(shfts,"pass"))

                shfts+=tag.getShiftPrev()
            
            if tNm in ("function" ,"model"):
                
                retBfr=currBfr
                
                if currBfr==self.wsmBfr:
                    shfts_wsm=shfts
                elif currBfr==self.wsbBfr:
                    shfts_wsb=shfts
                elif currBfr==self.wsoBfr:
                    shfts_wso=shfts
                elif currBfr==self.wscBfr:
                    shfts_wsc=shfts
                else:
                    shfts_run=shfts
                    
                shfts=shfts_fun
                currBfr=self.funBfr
                
            elif tNm in ("/function" ,"endfunction", "/model","endmodel")  :
                
                currBfr=retBfr#self.runBfr
                shfts_fun=shfts
                if currBfr==self.wsmBfr:
                    shfts=shfts_wsm
                elif currBfr==self.wsbBfr:
                    shfts=shfts_wsb
                elif currBfr==self.wsoBfr:
                    shfts=shfts_wso
                elif currBfr==self.wscBfr:
                    shfts=shfts_wsc
                else:
                    shfts=shfts_run
                
            elif tNm=="websocket:onmessage":
                
                retBfr=currBfr
                
                if currBfr==self.funBfr:
                    shfts_fun=shfts
                elif currBfr==self.wsbBfr:
                    shfts_wsb=shfts
                elif currBfr==self.wsoBfr:
                    shfts_wso=shfts
                elif currBfr==self.wscBfr:
                    shfts_wsc=shfts
                else:
                    shfts_run=shfts
                    
                shfts=shfts_wsm
                currBfr=self.wsmBfr
                
            elif tNm=="/websocket:onmessage" :
                
                currBfr=retBfr#self.runBfr
                shfts_wsm=shfts
                if currBfr==self.funBfr:
                    shfts=shfts_fun
                elif currBfr==self.wsbBfr:
                    shfts=shfts_wsb
                elif currBfr==self.wsoBfr:
                    shfts=shfts_wso
                elif currBfr==self.wscBfr:
                    shfts=shfts_wsc
                else:
                    shfts=shfts_run
                    
            elif tNm=="websocket":
                
                retBfr=currBfr
                
                if currBfr==self.funBfr:
                    shfts_fun=shfts
                elif currBfr==self.wsmBfr:
                    shfts_wsm=shfts
                elif currBfr==self.wsoBfr:
                    shfts_wso=shfts
                elif currBfr==self.wscBfr:
                    shfts_wsc=shfts
                else:
                    shfts_run=shfts
                    
                shfts=shfts_wsb
                currBfr=self.wsbBfr
                
            elif tNm=="/websocket" :
                
                currBfr=retBfr#self.runBfr
                shfts_wsb=shfts
                if currBfr==self.funBfr:
                    shfts=shfts_fun
                elif currBfr==self.wsmBfr:
                    shfts=shfts_wsm
                elif currBfr==self.wsoBfr:
                    shfts=shfts_wso
                elif currBfr==self.wscBfr:
                    shfts=shfts_wsc
                else:
                    shfts=shfts_run
                    
            elif tNm=="websocket:open":
                
                retBfr=currBfr
                
                if currBfr==self.funBfr:
                    shfts_fun=shfts
                elif currBfr==self.wsmBfr:
                    shfts_wsm=shfts
                elif currBfr==self.wsbBfr:
                    shfts_wsb=shfts
                elif currBfr==self.wscBfr:
                    shfts_wsc=shfts
                else:
                    shfts_run=shfts
                    
                shfts=shfts_wso
                currBfr=self.wsoBfr
                
            elif tNm=="/websocket:open" :
                
                currBfr=retBfr#self.runBfr
                shfts_wso=shfts
                if currBfr==self.funBfr:
                    shfts=shfts_fun
                elif currBfr==self.wsmBfr:
                    shfts=shfts_wsm
                elif currBfr==self.wsbBfr:
                    shfts=shfts_wsb
                elif currBfr==self.wscBfr:
                    shfts=shfts_wsc
                else:
                    shfts=shfts_run
                    
            elif tNm=="websocket:close":
                
                retBfr=currBfr
                
                if currBfr==self.funBfr:
                    shfts_fun=shfts
                elif currBfr==self.wsmBfr:
                    shfts_wsm=shfts
                elif currBfr==self.wsbBfr:
                    shfts_wsb=shfts
                elif currBfr==self.wsoBfr:
                    shfts_wso=shfts
                else:
                    shfts_run=shfts
                    
                shfts=shfts_wso
                currBfr=self.wscBfr
                
            elif tNm=="/websocket:close" :
                
                currBfr=retBfr#self.runBfr
                shfts_wsc=shfts
                if currBfr==self.funBfr:
                    shfts=shfts_fun
                elif currBfr==self.wsmBfr:
                    shfts=shfts_wsm
                elif currBfr==self.wsbBfr:
                    shfts=shfts_wsb
                elif currBfr==self.wsoBfr:
                    shfts=shfts_wso
                else:
                    shfts=shfts_run
                 
                    
            if(tag.getCompiled()!=""):       
                #shfts+=tag.getShiftPrev()
                currBfr.append(self.generateLine(shfts,tag.getCompiled())) 
                shfts+=tag.getShift()
                if(tag.isWriteThis()):
                    currBfr.append(self.generateLine(shfts, "this=self"))
            
           
        
        
        pyTxt=pyTxt.replace("$$RunBody$$","\n".join(self.runBfr))
        pyTxt=pyTxt.replace("$$Functions$$","\n".join(self.funBfr))
        pyTxt=pyTxt.replace("$$WSGetMessageBody$$","\n".join(self.wsmBfr))
        pyTxt=pyTxt.replace("$$WSBody$$","\n".join(self.wsbBfr))
        pyTxt=pyTxt.replace("$$WSGetMessageOpen$$","\n".join(self.wsoBfr))
        pyTxt=pyTxt.replace("$$WSGetMessageClose$$","\n".join(self.wscBfr))
        #$$WSGetMessageOpen$$
        
        out_file = None
       
        #self.xLemEnv.destPath="/Users/mgshow/Documents/workspace/XLEM/work/"
        #self.xLemEnv.destPath="/Users/mgshow/Documents/workspace/XLEM/work/"
        self.xLemEnv.destFile=self.do_GenerateClassName()+".py"
       
       
        try:
       
            #className=self.do_GenerateClassName()+"."+self.do_GenerateClassName()
       
            out_file = codecs.open(self.xLemEnv.destPath+self.xLemEnv.destFile, "w","utf-8")
            out_file.write(pyTxt)
            out_file.close()
            out_file=None
            
            btCode=py_compile.compile(self.xLemEnv.destPath+self.xLemEnv.destFile,doraise=True)
            
            
            # Store byte code into Server....
            
            return btCode
            
            #struct=__import__(self.do_GenerateClassName(),globals={}, locals={}, fromlist=[''],level=1)
            '''
            print("Carico modulo!")
            modl=imp.load_compiled(self.do_GenerateClassName(),btCode)
            print("modulo caricato!")
            clss=modl.__getattribute__(self.do_GenerateClassName())
            inst=clss()
            
            inst.doXLemService(None,None)
            '''
            
        except (IOError, OSError) as err:            
            
            print ("IO/OS ERROR 500 in parsing ",err)
            raise XLemException(err)
        
        except (Exception) as err:            
            
            print ("Exception/ERROR 500 in parsing", err)
            raise XLemException()
        
        finally:
            if out_file is not None:
                out_file.close()
       
        
        
        
        return pyTxt
    
    def generateLine(self, tabs, content):
        ret=""
        for i in range(0,tabs):
            ret+="    "
        ret+=content
        return ret
            
            
    
    def do_GenerateClassName(self):
        cnm=self.xLemEnv.sourcePath+self.xLemEnv.sourceFile
        return cnm.replace("/","_").replace(" ","_").replace(".","_").replace("-","_")
        
class XLemTag(object):
    
    TYPE_LEM = 1
    TYPE_TXT = 0
    
   
    def __init__(self, name="", content=""):
        self.name = name
        self.row = 0
        self.col = 0
        self.content = content
        self.type = 0
        self.compiled = ""
        self.shift=0
        self.shiftPrev=0
        self.writePass=False
 
    def getName(self):
        return self.name
        
    def getContent(self):    
        return self.content.replace('\n',' ').replace('\r','')
    
    def getOriginalContent(self):    
        return self.content
    
    def getCompiled(self):
        return self.compiled
    
    def getShift(self):
        return self.shift
    
    def getShiftPrev(self):
        return self.shiftPrev
    
    def setShift(self,shift):
        self.shift=shift
        
    def setShiftPrev(self,shiftPrev):
        self.shiftPrev=shiftPrev    
    
    def setCompiled(self, value):
        self.compiled=value
        
    def isLemTag(self):
        return type == self.TYPE_LEM
    
    def isWritePass(self):
        return self.writePass
    
    def isWriteThis(self):
        return self.writeThis
    
 
class XLemParserEnvironment:
        
        def __init__(self):
            
            self.sourcePath = ""
            self.sourceFile = ""
            self.destPath = ""
            self.destFile = ""
            self.dependencies = {} 
            
class XLemParserOptions:
    
        def __init__(self):
            
            self.econding = "UTF-8"
            self.enableComments = True
            
