from runtime.core.config import MetaType, VerifierConfig
from runtime.core.event import Event, AgentEvent, EventLog
from typing import List

class Check:
    def __init__(self, type:MetaType, trigger:int, expected):
        self.type = type
        self.trigger = trigger
        self.expected = expected
    
    def _get_agent_events_after_trigger(self, event_list):
        trigger_time = event_list[self.trigger].timestamp
        return [e for e in event_list 
                if isinstance(e, AgentEvent) and e.timestamp >= trigger_time]
        
    def verify(self, event_list:List[Event]):
        agent_events = self._get_agent_events_after_trigger(event_list)
        match self.type:
            case MetaType.tool:
                found = any(e.tool == self.expected for e in agent_events)
                return CheckResult(
                    name=f"toolCheck after event {self.trigger}",
                    passed=found,
                    meta_type="tool",
                    expected=f"{self.expected}",
                    actual=f"{[e.tool for e in agent_events]}"
                )
            case MetaType.arg:
                found = any(
                    all(e.args.get(k) == v for k, v in self.expected.items())
                    for e in agent_events
                )
                return CheckResult(
                    name=f"argCheck after event {self.trigger}",
                    passed=found,
                    meta_type="arg",
                    expected=f"{self.expected}",
                    actual=f"{[e.args for e in agent_events]}"
                )
            case MetaType.result:
                found = any(e.result == self.expected for e in agent_events)
                return CheckResult(
                    name=f"resultCheck after event {self.trigger}",
                    passed=found,
                    meta_type="result",
                    expected=f"{self.expected}",
                    actual=f"{[e.result for e in agent_events]}"
                )
            case MetaType.sequence:
                tools_called = [e.tool for e in agent_events]

                it = iter(tools_called)
                found = all(t in it for t in self.expected)

                return CheckResult(
                    name=f"sequenceCheck after event {self.trigger}",
                    passed=found,
                    meta_type="sequence",
                    expected=f"{self.expected}",
                    actual=f"{[e.tool for e in agent_events]}"
                ) 
            case MetaType.content:
                return CheckResult(name=f"contentCheck after event {self.trigger}", passed=True, meta_type="content", expected="soft check not implemented", actual="")

class Verifier:
    def __init__(self, checks):
        self.checks = checks


    def verify(self, eventLog:EventLog):
        event_list = eventLog.to_list()
        results = [check.verify(event_list) for check in self.checks]
        return VerificationResult(results)

class CheckResult:
    def __init__(self, name, passed, meta_type, expected, actual):
        self.name = name
        self.passed = passed      # bool
        self.meta_type = meta_type
        self.expected = expected
        self.actual = actual
    
    def __repr__(self):
        if self.passed:
            return f"✅ : {self.name}"
        return f"❌ : {self.name}\n{self.actual}\n{self.expected}"
        

class VerificationResult:
    def __init__(self, results: list[CheckResult]):
        self.results = results
        self.passed = all(r.passed for r in results)
        self.score = sum(r.passed for r in results) / len(results)
    
    def __repr__(self):
        intro = f"Passed: {sum(r.passed for r in self.results)}/{len(self.results)}\n\n"
        ind_results = "\n".join([repr(res) for res in self.results])
        return intro + ind_results

