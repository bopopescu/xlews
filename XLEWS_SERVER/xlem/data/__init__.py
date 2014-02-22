import json as __JSON__


class XLemModelBean(object):
    '''
    Define a Model under MVC environment...
    '''

    def __write_value__(self, v, bfr):
        
        if isinstance(v,int):
            bfr.append(str(v))
            return
        
        bfr.append("\"")    
        bfr.append(v.replace("\"","\\\""))
        bfr.append("\"")
        
        
        pass

    def __initModelFields__(self) : 
        # virtual method...
        pass

    def __init__(self):
        self.__fieldz__=[]
        self.__initModelFields__()
        pass
    
    def __addField__(self, name, fieldValue):
        self.__dict__.update({name:fieldValue})
        self.__fieldz__.append(name)
        pass
    
    def tojson(self):
        
        ret=[]
        ret.append("{")
        i=0
        for x in self.__fieldz__:
            
            if i>0:
                ret.append(",")
            i=i+1
            
            ret.append("\"")
            ret.append(x)
            ret.append("\"")
            ret.append(" : ")
            
            
            v=self.__dict__.get(x)
            
            if isinstance(v,XLemModelBean):
                ret.append(v.tojson())
            else:
                self.__write_value__(v, ret)
                
        ret.append("}")
        return "".join(ret)
        pass
    
        