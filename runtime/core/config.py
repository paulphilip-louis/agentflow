import os
import yaml
from enum import Enum
from pydantic import BaseModel, NonNegativeInt, Field
from typing import List, Dict, Any



SCENARIOS_FOLDER = "/runtime/scenarios"

class SourceConfig(str, Enum):
    """
    Source of an event
    """
    USER = "user_message"
    ENVIRONMENT = "env_event"
    AGENT = "agent_call"


class ScenarioEvent(BaseModel):
    """An event defined in the YAML scenario file.
    
    - type determines which Runtime Event subclass to create:
        user_message → UserEvent
        env_event    → EnvEvent
    - AgentEvents are NEVER in the YAML — they are created at runtime
      when the agent calls tools.
    """
    type: SourceConfig
    scheduled_time: int = Field(ge=0)
    payload: str
 
    # Optional fields for env events
    app: str = "system"
    event_type: str = "scheduled"


class MetaType(str, Enum):
    """
    Type of a check - determines how a check is executed
    """
    tool = "toolCheck" # did the agent call the right tool?
    arg = "argCheck" # did the agent call the tool with the right arguments?
    result = "resultCheck" # did the agent return the correct result?
    sequence = "sequenceCheck" # did the agent execute its actions in the correct order?
    content = "contentCheck"    # soft, LLM-as-a-judge

class CheckConfig(BaseModel):
    """
    Single check in YAML scenario file

    - meta_type: the verification strategy (toolCheck, argCheck, etc.)
    - trigger: index of the scenario event after which to look for
      agent actions in the EventLog
    - expected: what we expect to find — shape depends on meta_type:
        toolCheck:     str            (tool name)
        argCheck:      dict           (argument key-value pairs)
        resultCheck:   Any            (expected return value)
        sequenceCheck: list[str]      (ordered list of tool names)
        contentCheck:  str            (evaluation prompt for LLM judge)
    """
    meta_type: MetaType
    trigger: int                # index of trigger event
    expected: Any               # flexible depending on meta_type

class VerifierConfig(BaseModel):
    checks:List[CheckConfig]

class AppConfig(BaseModel):
    initial_state: dict = {}
    model_config = {"extra": "allow"}

class ScenarioConfig(BaseModel):
    name:str
    description:str
    apps: Dict[str, AppConfig]
    events: List[ScenarioEvent]
    verifier: VerifierConfig
