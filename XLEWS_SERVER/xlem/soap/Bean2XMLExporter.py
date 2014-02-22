'''
Created on Oct 22, 2013

@author: mgshow
'''

def is_primitive(o):
    if isinstance(o,(str,int,float,bool)):
        return True
    return False

def is_array(o):
    if (isinstance(o,(list))):
        return True
    return False

def newTag(bfr,name):

    bfr.append("<")
    bfr.append(name)
    bfr.append(">")
    
def closedTag(bfr,name):

    bfr.append("</")
    bfr.append(name)
    bfr.append(">")

def Model(clazz):
    
    fl=clazz.__fieldList__
    
    for f in fl:
        
        print ("CAMPOZZO: ",f, fl.get(f))
        
        
        pass
    
    
    return clazz
    pass

def Fields(fieldList):
    def decorator(func):
        func.__fieldList__=fieldList
        print ("FIELD LIST:=",fieldList)
        return func
    #print("Campozzo"+clazz.__name__)
    return decorator
    pass

def WebService(clazz):
    clazz.__ws_Methods__={}
    return clazz
    
    pass

def WebMethod(name:str=None, namespace:str=None, returnType=str):
    def decorator(func):
        print ("Aggiungo un metodo!",name, namespace,func.__name__)
        
        def wrapper(*args, **kwargs):
            print(args,kwargs)
            return func(*args, **kwargs)
        
        #print(func.__module__)
        #print(func.__args__)
        
        #func.__self__.__ws_Methods__.update(name,func)
        return wrapper
        pass
    return decorator
    pass

class SOAPBean(object):
    
    def __init__(self):
        
        self.__fieldNames__=[]
        self.__fields__={}
        
        pass
    
    def addField(self, name:str, tp):
        
        self.__fieldNames__.append(name)
        self.__fields__.update({name: tp})
        
        pass

class SOAPContext(object):
    
    def __init__(self):
        
        __beans__={}
        
        pass
    
    def addBean(self, bean:SOAPBean):
        
        pass
        


class Bean2XMLExporter(object):
    
    def __init__(self):
        
        
        pass
    
    def export(self, bfr, obj, options):
    
        #d=obj.__dict__
        if not hasattr(obj,'__fieldList__'):
            return
        
        d=obj.__fieldList__
        
        
        for f in d.keys():
            if hasattr(obj,f):
                o=getattr(obj,f)
            else:
                o=None    
            
             
            self.exportField(bfr, f, o, options)
            
            pass
            
        pass
    
        
    
    def exportField(self, bfr, f, o, options):
    
        newTag(bfr,f)
        
        if is_primitive(o):
            
            self.exportPrimitive(bfr, f, o, options)
            
        elif is_array(o):
            
            for v in o:
                
                if is_primitive(v):
                    self.exportArrayOfPrimitive(bfr, "item", v, options)
                else:
                    self.exportArrayOfComplex(bfr, f, v, options)
                
        else:
            
            self.exportComplex(bfr,f,o,options)    
       
        
        closedTag(bfr,f)
            
        pass
    
    
    def exportPrimitive(self, bfr, f, o, options):
    
        bfr.append(str(o))

        pass
    
    def exportArrayOfPrimitive(self, bfr, f, o, options):
    
        newTag(bfr,f)
        bfr.append(str(o))
        closedTag(bfr,f)
    
        pass
    
    def exportComplex(self, bfr, f, o, options):
    
        self.export(bfr,o,options)
        
        pass

    pass

    def exportArrayOfComplex(self, bfr, f, o, options):
        
        
        if isinstance(o,list):
            newTag(bfr,"item")
            i=0
            for xx in o:
                self.exportArrayOfPrimitive(bfr, "item"+str(i), xx, options)
                i=i+1
            pass
            closedTag(bfr,"item")
        else:
            bfr.append("<"+str(o.__class__.__name__)+">")
            self.export(bfr,o,options)
            bfr.append("</"+str(o.__class__.__name__)+">")
        
        
        pass

    pass


class WSDLCreator(object):
    
    
    def __init__(self):
        
        self.methods={}
        self.baseClass=None
        
        
        pass
    
    def setBaseClass(self, baseClass):
        self.baseClass=baseClass
    
    pass