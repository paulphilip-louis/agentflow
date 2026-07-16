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
        """
        Adds an event named {title} to the calendar at {date}.
        Arguments:
        - date: str.
        - title: str.
        Output:
        - Status message: str
        """
        self.events.append((date, title))
        return f"Successful added event {title} on {date}"
   
    
   
class DocumentStore(App):
    def __init__(self):
        super().__init__()
        self.documents = {}
    
    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for doc in initial_state.get("documents", []):
            instance.documents[doc["name"]] = doc["content"]
        return instance

    @tool()
    def list_doc(self):
        """
        Enables to list all documents
        """
        document_list = "List of documents found: \n"
        for k in self.documents.keys():
            document_list += f"\n - {k}"
        return document_list
    
    @tool()
    def add_doc(self, name, content):
        """
        Add a new document to the Document Store
        Arguments:
        - name: str. Name of the document
        - content: str. Content of the document
        Output:
        - Status message: str
        """
        self.documents[name] = content
        return f"Document {name} added"

    @tool()
    def retrieve_doc(self, name):
        """
        Retrieves a document in the document store by its name.
        Arguments:
        - name: str. Name of the document
        Output:
        - content: str. Content of the document
        """
        if name not in self.documents:
            return "Document not found. List all documents before to find the name you're looking for."
        content = self.documents[name]
        return f"Document {name} found: \n Content: {content}"
    
    @tool()
    def generate_invoice(self, content):
        """
        Generates invoice. A particular case of add_doc.
        Arguments:
        - content: str. What to write in the invoice.
        Returns:
        - Status message: str. 
        """
        self.documents["invoice.pdf"] = content
        return "Invoice created with the intended content. File name: invoice.pdf"


