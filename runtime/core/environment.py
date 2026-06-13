from runtime.core.event import Event, AgentEvent, EventLog, EventQueue
from runtime.core.utils import Status


class Environment:
    def __init__(self, apps):
        self.apps = apps # apps will be a dict {app_name: app object}
        self.clock = 0
        self.eventLog = EventLog()
        self.eventQueue = EventQueue()
    
    def execute_tool(self, app_name, tool_name, **kwargs):
        method = self.apps[app_name].tools[tool_name]
        try:
            result = method(**kwargs)
            event = AgentEvent(app=app_name, tool=tool_name, args=kwargs, result=result)
            event.status = Status.COMPLETED
        except Exception as e:
            event = AgentEvent(app=app_name, tool=tool_name, args=kwargs, result=str(e))
            event.status = Status.FAILED
        event.timestamp = self.clock
        self.eventLog.add(event)
        return event.result
