import yaml
from runtime.core.config import ScenarioConfig, SourceConfig, MetaType  # ton modèle Pydantic top-level
from runtime.core.app_registry import APP_REGISTRY
from runtime.core.event import EnvEvent, UserEvent, AgentEvent
from runtime.core.utils import Status
from runtime.core.verifier import Verifier, Check

class Scenario:
    def __init__(self, path):
        with open(path) as f:
            raw = yaml.safe_load(f)
        
        self.config = ScenarioConfig(**raw)  # Pydantic valide tout d'un coup
        self.apps = self._build_apps()
        self.events = self._build_events()
        self.verifier = Verifier([
            Check(
                type=MetaType(c.meta_type),
                trigger=c.trigger,
                expected=c.expected
            )
            for c in self.config.verifier.checks
        ])

    def _build_apps(self):
        apps = {}
        for name, app_config in self.config.apps.items():
            app_class = APP_REGISTRY[name]
            app = app_class.from_config(app_config.initial_state)
            apps[name] = app
        return apps

    def _build_events(self):
        events = []
        for e in self.config.events:
            if e.type == SourceConfig.USER:
                event = UserEvent(message=e.payload)
                event.scheduled_time = e.scheduled_time
                events.append(event)
            elif e.type == SourceConfig.ENVIRONMENT:
                event = EnvEvent(app="system", event_type="scheduled", message=e.payload)
                event.scheduled_time = e.scheduled_time
                events.append(event)
        return events
    
    
    
    def __repr__(self):
        apps = "Apps: " + ";".join(app_name for app_name in self.apps.keys())
        return apps + "\n\n" + repr(self.events)