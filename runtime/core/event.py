from uuid import uuid4, UUID
from runtime.core.utils import Status
import heapq
import inspect

    

class Event:
    """Abstract class common to each event"""
    def __init__(self, status: Status):
        self.id             = uuid4()
        self.status         = status
        self.timestamp      = None
        self.scheduled_time = None


class UserEvent(Event):
    def __init__(self, message: str):
        super().__init__(status=Status.PENDING)
        self.message = message
    
    def __repr__(self):
        intro = f"Event : t={self.timestamp} | "  
        body  = " | ".join([str(self.id), "USER", self.message])
        return intro + body

class AgentEvent(Event):
    def __init__(self, app: str, tool: str, args: dict, result=None):
        super().__init__(status=Status.PENDING)
        self.app = app
        self.tool = tool
        self.args = args
        self.result = result    # filled after execution

    def __repr__(self):
        intro = f"Event : t={self.timestamp} | "  
        body  = " | ".join([str(self.id), "AGENT", self.app, self.tool, str(self.args), str(self.result)])
        return intro + body
    
class EnvEvent(Event):
    def __init__(self, app: str, event_type: str, message: str):
        super().__init__(status=Status.PENDING)
        self.app = app
        self.event_type = event_type  # "notification", "new_file", etc.
        self.message = message

    def __repr__(self):
        intro = f"Event : t={self.timestamp} | "  
        body  = " | ".join([str(self.id), "ENVIRONMENT", self.app, self.event_type, self.message])
        return intro + body

class EventLog:
    def __init__(self,):
        self.events = {}
    
    def __repr__(self):
        n = len(self.events)
        return f"EventLog ({n} events):\n" + '\n'.join([repr(event) for event in self.events.values()])
        
    
    def add(self, event:Event):
        self.events[event.id] = event

    def get(self, event_id:UUID):
        return self.events[event_id]
    
    def filter(self, event_type=None):
        """event_type: UserEvent, AgentEvent, or EnvEvent"""
        selected = [e for e in self.events.values()
                    if event_type is None or isinstance(e, event_type)]
        return sorted(selected, key=lambda e: e.timestamp)
            
    def to_list(self):
        serialized = list(self.events.values())
        return sorted(serialized, key=lambda event: event.timestamp)

class EventQueue:
    def __init__(self,):
        self.heap = []
        self._counter = 0
    
    def push(self, event, scheduled_time):
        heapq.heappush(self.heap, (scheduled_time, 0, event))
        self._counter += 1
    
    def pop(self):
        return heapq.heappop(self.heap)[2]

    def peek(self):
        return self.heap[0][2]
    
    def is_empty(self):
        return not self.heap