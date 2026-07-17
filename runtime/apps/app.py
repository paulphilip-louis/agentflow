import inspect

def tool():              
    def decorator(func):        
        func._is_tool = True    
        return func             
    return decorator

class App:
    def __init__(self):
        self.tools = {}
        for name, member in inspect.getmembers(self, callable):
            if getattr(member, "_is_tool", False):
                self.tools[name] = member
    