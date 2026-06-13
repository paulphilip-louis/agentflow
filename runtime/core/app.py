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
    

class Calendar(App):
    def __init__(self):
        super().__init__()
        self.events = []

    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for item in initial_state.get("events", []):
            instance.events.append((item["date"], item["title"]))
        return instance
   
    @tool()
    def add_event(self, date, title):
        self.events.append((date, title))
        return f"Successful added event {title} on {date}"
   
    
   
class DocumentStore(App):
    def __init__(self):
        super().__init__()
        self.documents = {}
    
    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for name, content in initial_state.get("documents", {}):
            instance.documents[name] = content
        return instance

    
    @tool()
    def add_doc(self, name, content):
        self.documents[name] = content
        return f"Document {name} added"

    @tool()
    def retrieve_doc(self, name):
        return self.documents[name]
    
    @tool()
    def generate_invoice(self, content):
        self.documents["invoice"] = content
        return "Invoice created"


