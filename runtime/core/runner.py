from runtime.core.scenario import Scenario, APP_REGISTRY
from runtime.core.environment import Environment
from runtime.core.utils import Status
from runtime.core.agent import create_env_agent
from runtime.core.event import UserEvent

class Runner:
    def __init__(self, verifier):
        self.verifier = verifier

    def run(self, scenario:Scenario):
        print("Run started")
        print("Creating environment...")
        self.env = Environment(scenario.apps)
        print("Initializing agent...")
        self.agent = create_env_agent(self.env)
        
        print("Configuring scenario...")
        for event in scenario.events:
            self.env.eventQueue.push(event, scheduled_time=event.scheduled_time)
        
        while not self.env.eventQueue.is_empty():
            next_event = self.env.eventQueue.pop()
            self.env.clock = next_event.scheduled_time
            next_event.timestamp = self.env.clock
            next_event.status = Status.COMPLETED
            self.env.eventLog.add(next_event)
            if isinstance(next_event, UserEvent):
                result = self.agent.invoke({"messages":[("user", next_event.message)]})
            
        
        return self.verifier.verify(self.env.eventLog)

        
