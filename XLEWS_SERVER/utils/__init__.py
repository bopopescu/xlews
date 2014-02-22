import hashlib
import random
import base64
from time import sleep as pause
import json as __JSON__

true=True
false=False
null=None

#mobile api
def is_android(userAgent):
    if isblank(userAgent):
        return false
    return userAgent.rfind("android")>=0

def is_blackberry(userAgent):
    if isblank(userAgent):
        return false
    return userAgent.rfind("blackberry")>=0

def is_iphone(userAgent):
    if isblank(userAgent):
        return false
    return userAgent.rfind("iphone")>=0

def is_ipad(userAgent):
    if isblank(userAgent):
        return false
    return lowercase(userAgent).rfind("ipad")>=0

def is_windows_ce(userAgent):
    if isblank(userAgent):
        return false
    return userAgent.rfind("windows ce")>=0

def ismobile(userAgent):
    if isblank(userAgent):
        return false
    uag=lowercase(userAgent)
    for dvc in ('mobile','android','blackberry','iphone','windows_ce'):
        if uag.rfind(dvc)>=0:
            return true
    
    return false


def lowercase(s):
    
    if type(s) is str:
        return s.lower()
    return repr(s).lower()

def uppercase(s):
    
    if type(s) is str:
        return s.lower()
    return repr(s).upper()


def htmlformat(html):
    
    if type(html) is not str:
        x=repr(html)
    else:
        x=html
    
    return x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"","&quot;")
    
def htmlformatspecial(html):
    
    #s=html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"","&quot;")
    
    s=htmlformat(html)
    
    s=s.replace("\n","<br>").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
    
    return s

def sqlformat(sql):
    
    return sql.replace("'","\'").replace("\\","\\\\")    

def tostring(s):
    
    if type(s) is str:
        return s
    elif type(s) is list:
        return "".join(s)
    return repr(s)

def tointeger(s):
    
    if type(s) is int:
        return s
    
    try:
        return int(s)
    except Exception:
        return 0

def tolong(s):
    
    try:
        return int(s)
    except Exception :
        return 0

def todouble(s):
    
    try:
        return float(s)
    except Exception:
        return 0.0

def toboolean(s):
    return equalsnocase(s,'true')

def tofloat(s):
    
    try:
        return float(s)
    except Exception:
        return 0.0

def trim(s):
    return s.strip()


def isnotnull(s):
    return not s== None

def isnull(s):
    return s == None

def notisnull(s):
    return isnotnull(s)

def jQueryLink(icon, link, pos):
    if notisblank(icon):
        return "<a href='"+link+"' class='ui-state-default ui-corner-all onlyIcon "+pos+"' ><span class='ui-icon "+icon+"'></span></a>"
    return ""

def jQueryButton(icon, link, pos):
    if notisblank(icon):
        "<button onclick='"+link+"' style='margin:0 1px' class='ui-state-default ui-corner-all onlyIcon "+pos+"' ><span class='ui-icon "+icon+"'></span></button>"
    return ""    

def equals(s1,s2):
    
    if type(s1) is str and type(s2) is str:
        return s1==s2
    
    return tostring(s1)==tostring(s2)

def equalsnocase(s1,s2):
    return tostring(s1).upper()==tostring(s2).upper()

def notequals(s1,s2):
        return not equals(s1,s2)    

def isblank(s):
    
    if type(s) is str:
        return s.strip()==""
    
    print ("Considero Caso No stringa : None")
    if s == None:
       
        return True
    
    return False 
    
def isnotblank(s):
    return not isblank(s)

def notisblank(s):
    return not isblank(s)

def MD5(str_value, str_encoding="utf-8"):
    try:
        m=hashlib.md5()
        m.update(bytes(str_value,str_encoding))
        return m.hexdigest()
    except Exception:
        return str_value            

def tojson(obj):
    try:
        return __JSON__.dumps(obj.__dict__)
    except Exception as e:
        print("ERRORE:",e)
        return "{}"

def fromjson(s):
    try:
        return __JSON__.loads(s)
    except:
        return None
            
def generateKEY():
    return MD5(str(random.getrandbits(256)))
    #x=base64.b64encode(hashlib.sha256( str(random.getrandbits(256)) ).digest(), random.choice(['rA','aZ','gQ','hH','hG','aR','DD'])).rstrip('==')
    #return x