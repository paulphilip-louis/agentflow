from runtime.core.scenario import Scenario, APP_REGISTRY
from runtime.core.environment import Environment
from runtime.core.utils import Status

def mock_agent(payload):
    if payload=="Generate the October invoice for client Acme using the timesheet and tariff grid.":
        return [
            {"app":"document_store", "tool":"retrieve_doc", "kwargs":{"name":"timesheet_october.csv"}},
            {"app":"document_store", "tool":"retrieve_doc", "kwargs":{"name":"tariff_grid.json"}},
            {"app":"document_store", "tool":"generate_invoice", "kwargs":{"name":"tariff_grid.json"}}
        ]
    else:
        return []

class Runner:
    def __init__(self, agent, verifier):
        self.agent = agent
        self.verifier = verifier

    def run(self, scenario:Scenario):
        env = Environment(scenario.apps)
        for event in scenario.events:
            env.eventQueue.push(event, scheduled_time=event.scheduled_time)
        
        while not env.eventQueue.is_empty():
            next_event = env.eventQueue.pop()
            env.clock = next_event.scheduled_time
            next_event.timestamp = env.clock
            next_event.status = Status.COMPLETED
            env.eventLog.add(next_event)
            tool_calls = self.agent(next_event.message)
            for tool_call in tool_calls:
                app = tool_call["app"]
                tool = tool_call["tool"]
                kwargs = tool_call["kwargs"]
                env.execute_tool(app_name=app, tool_name=tool, **kwargs)
        
        return self.verifier.verify(env.eventLog)

        
