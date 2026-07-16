from runtime.core.event import Event, AgentEvent, EventLog, EventQueue
from runtime.core.utils import Status
from langchain_core.tools.structured import StructuredTool
from functools import wraps


class Environment:
    def __init__(self, apps):
        self.apps = apps # apps will be a dict {app_name: app object}
        self.clock = 0
        self.eventLog = EventLog()
        self.eventQueue = EventQueue()
        self.tools = self.make_langchain_tools()
        
    
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
        self.clock += 1
        self.eventLog.add(event)
        return event.result
    
    def make_langchain_tools(env):
        lc_tools = []
        for app_name, app in env.apps.items():
            for tool_name, method in app.tools.items():
                def make_wrapper(a=app_name, t=tool_name, m=method):
                    @wraps(m)
                    def wrapper(**kwargs):
                        return env.execute_tool(app_name=a, tool_name=t, **kwargs)
                    return wrapper

                wrapper = make_wrapper()

                lc_tools.append(StructuredTool.from_function(
                    func=wrapper,
                    name=f"{app_name}__{tool_name}",
                    description=method.__doc__ or f"{tool_name} on {app_name}",
                ))
        return lc_tools
