from runtime.core.scenario import Scenario
from runtime.core.runner import Runner, mock_agent


def main():
    scenario = Scenario("runtime/scenarios/test.yaml")
    runner = Runner(agent=mock_agent, verifier=scenario.verifier)
    result = runner.run(scenario)
    print(result)

if __name__ == "__main__":
    main()
