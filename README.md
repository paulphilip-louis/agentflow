# Agentflow

**Collaborative evaluation environments for AI agents.**

Agentflow is a platform that lets AI engineers and domain experts co-create evaluation scenarios for AI agents. Engineers instrument their agents via a CI/CD-integrated CLI; domain experts describe their business processes through an intuitive interface. Both sides converge at evaluation time, combining technical metrics (latency, token usage, tool call traces) with business-relevant verification criteria.

> ⚠️ **Early-stage MVP** — this repository contains a working runtime, CLI, and dashboard prototype. Not production-ready.

---

## Why Agentflow

Current agent evaluation is broken in two ways. Engineers test with synthetic benchmarks that don't reflect real business processes. Domain experts can't express their expectations in a format that's programmatically verifiable. Agentflow bridges this gap.

The core insight: evaluation scenarios should be **declarative** (YAML files a non-engineer can read), **reproducible** (deterministic simulated environments), and **structured** (verification goes beyond pass/fail to show exactly which step failed and why).

---

## Architecture

Agentflow is organized in two main modules.

```
agentflow/
├── runtime/                    # Python — evaluation engine
│   ├── core/
│   │   ├── app.py              # Base App class + @tool decorator
│   │   ├── agent.py            # Langgraph agent
│   │   ├── event.py            # Event hierarchy (UserEvent, AgentEvent, EnvEvent)
│   │   ├── environment.py      # Simulated environment: apps + clock + execution
│   │   ├── scenario.py         # YAML loader → runtime objects (via Pydantic)
│   │   ├── verifier.py         # Check engine: toolCheck, argCheck, resultCheck, sequenceCheck, contentCheck
│   │   ├── runner.py           # Orchestrator: loads scenario, runs agent, returns results
│   │   └── config.py           # Pydantic models for YAML validation
│   └── apps/                   # Concrete App implementations (e.g. DocumentStore)
│
├── dashboard/                  # React — evaluation dashboard
│   ├── src/
│   │   └── App.jsx             # Interactive results viewer
│   ├── public/
│   │   └── results.json        # Results of a run 
├── scenarios/                  # Scenarios as YAML files
├── cli.py.                     # CLI entry point
│
└── README.md
```

### Three-layer design

**Layer 1 — Environment Runtime.** An event-driven, deterministic simulation engine inspired by Meta's [ARE (Agents Research Environments)](https://github.com/facebookresearch/meta-agents-research-environments) framework. The runtime manages Apps (stateful tool interfaces), Events (timestamped, typed, logged), an Environment (simulated clock + event queue), and Scenarios (declarative YAML descriptions of test cases). Time is simulated, not real — a scenario spanning hours executes in seconds.

**Layer 2 — Verifier Engine.** A hierarchical verification system that maps directly to the JSON rubric describing a business process. Each check has a `meta_type` that determines the verification strategy:

| Meta-type | What it checks | Method |
|-----------|---------------|--------|
| `toolCheck` | Did the agent call the right tool? | Exact match on tool name |
| `argCheck` | Did the agent pass the right arguments? | Key-value comparison on args dict |
| `resultCheck` | Did the tool return the expected value? | Equality check on result |
| `sequenceCheck` | Were actions performed in the right order? | Subsequence matching |
| `contentCheck` | Is the output qualitatively correct? | LLM-as-a-judge (planned) |

Each check is anchored to a **trigger** — a scenario event after which the agent's actions are examined. This makes verification context-aware: "after the user asked for an invoice, did the agent retrieve the right files?"

**Layer 3 — CI/CD Integration.** A CLI that runs scenarios and produces structured results (terminal output + JSON). Designed to plug into GitHub Actions, GitLab CI, or any pipeline.

A visual:
[agentflow_architecture](public/agentflow_architecture.svg)

### Event hierarchy

Events follow a subclass pattern where the type determines the available fields:

```
Event (base: id, status, timestamp)
├── UserEvent (message)
├── AgentEvent (app, tool, args, result)
└── EnvEvent (app, event_type, message)
```

`source` and `op_type` are not stored on the event — source is determined by the subclass, and op_type is carried by the `@tool` decorator on the App method. This eliminates an entire class of inconsistency bugs.

### App system

Apps are Python classes that inherit from `App`. Methods decorated with `@tool(op_type=OpType.WRITE)` or `@tool(op_type=OpType.READ)` are automatically discovered via introspection at instantiation time. The decorator marks the function at class definition time; `App.__init__` scans for marked methods and builds the tool registry.

```python
class DocumentStore(App):
    def __init__(self):
        super().__init__()
        self.documents = {}

    @tool(op_type=OpType.WRITE)
    def add_document(self, name, content):
        self.documents[name] = content
        return f"Document '{name}' stored."

    @tool(op_type=OpType.READ)
    def retrieve_doc(self, name):
        return self.documents.get(name, "Not found.")
```

---

## Inspiration

The runtime architecture is directly inspired by Meta's **ARE (Agents Research Environments)** paper ([arXiv, September 2025](https://github.com/facebookresearch/meta-agents-research-environments)). ARE introduces five core abstractions — Apps, Environments, Events, Notifications, and Scenarios — for scalable creation of agent evaluation environments. Agentflow adopts this conceptual framework and extends it with:

- **Declarative YAML scenarios** editable by non-engineers (ARE scenarios are Python code).
- **A hierarchical verifier with typed checks** (toolCheck, argCheck, resultCheck, sequenceCheck, contentCheck) rather than ARE's single oracle-action matching approach.
- **A trigger-based verification model** that anchors checks to specific scenario events, making it explicit when and what to verify.
- **Pydantic-validated configuration** for scenario files, catching errors at parse time.

---

## Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.11+, Pydantic, PyYAML |
| CLI | argparse, ANSI terminal formatting |
| Dashboard | React 18, inline CSS, JSX |
| Scenarios | YAML |
| Event queue | `heapq` (standard library) |
| IDs | `uuid4` (standard library) |
| Agents | Langchain, Langgraph |

No heavy frameworks. No external databases. The runtime is dependency-light by design — it should be easy to install, easy to embed in CI, and easy to understand.

---

## Quickstart

### Prerequisites
 
- Python 3.11+
- Node.js 18+ and npm
- An OpenAI API key (for LLM-powered agent runs)

### 1. Clone and install the backend
 
```bash
git clone https://github.com/paulphilip-louis/agentflow.git
cd agentflow
```

Create a `.env` file at the project root:
 
```
OPENAI_API_KEY=sk-your-key-here
```

We are using ```uv``` package manager. To get started:

```bash
uv init
uv sync
source .venv/bin/activate
```

### 2. Run a scenario from the CLI

Run a single scenario:
```bash
python cli.py run --scenario scenarios/invoice_generation.yaml
```

Run the full test suite:

```bash
python cli.py run --suite scenarios/ --output dashboard/public/results.json
```

List available scenarios:

```bash
python cli.py list --suite scenarios/
```

Example output:

```
  ___                __  __ __              
  / _ |___ ____ ___  / /_/ _/ /___ __  __
 / __ / _ `/ -_) _ \/ __/ _/ / _ \  |/| /
/_/ |_\_, /\__/_//_/\__/_//_/\___/__,__/  
     /___/                            v0.1.0

────────────────────────────────────────────────────────

  Suite  scenarios
  Scenarios  3 found

────────────────────────────────────────────────────────

  [1/3] contract_review  Run started
❌ FAIL  3/4  9.48s
  [2/3] email_triage  Run started
✅ PASS  3/3  5.11s
  [3/3] invoice_generation  Run started
✅ PASS  4/4  11.09s

────────────────────────────────────────────────────────

  Suite Result  2/3 scenarios passed
  Checks       10/11 total checks
  Score        ███████████████████████████░░░  91%
```

### Visualizing results
If you don't have Node.js installed, get it from [nodejs.org](https://nodejs.org/) (LTS version recommended).
 
Create the React app (first time only):
 
```bash
npm create vite@latest dashboard -- --template react
cd dashboard
npm install
```
 
Copy the dashboard files into the project:
 
```bash
cp path/to/Dashboard.jsx dashboard/src/Dashboard.jsx
cp path/to/Dashboard.css dashboard/src/Dashboard.css
```
 
Edit `dashboard/src/App.jsx` to use the dashboard:
 
```jsx
import Dashboard from './Dashboard'
import './Dashboard.css'
 
function App() {
  return <Dashboard />
}
 
export default App
```

Once results are saved in a json file, make sure your results are at ```dashboard/public/results.json```.

Then, start the dashboard:
 
```bash
cd dashboard
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Writing a scenario

Scenarios are YAML files with three sections: apps (initial state), events (what happens), and verifier (what to check).

```yaml
name: "invoice_generation"
description: "Agent must gather files, compute tariffs, generate invoice"

apps:
  document_store:
    initial_state:
      documents:
        - id: "doc_1"
          name: "timesheet_october.csv"
          content: "employee,hours\nAlice,160\nBob,140"
        - id: "doc_2"
          name: "tariff_grid.json"
          content: '{"hourly_rate": 150}'

events:
  - type: "user_message"
    scheduled_time: 0
    payload: "Generate the October invoice for client Acme."

  - type: "env_event"
    scheduled_time: 30
    app: "email"
    event_type: "notification"
    payload: "Client updated their billing address."

verifier:
  checks:
    - meta_type: "toolCheck"
      trigger: 0
      expected: "retrieve_doc"

    - meta_type: "argCheck"
      trigger: 0
      expected:
        name: "timesheet_october.csv"

    - meta_type: "sequenceCheck"
      trigger: 0
      expected:
        - "retrieve_doc"
        - "retrieve_doc"
        - "generate_invoice"
```
---

## Roadmap
 
- [x] Event-driven runtime with simulated clock
- [x] YAML scenario loader with Pydantic validation
- [x] Verifier engine (5 check types)
- [x] CLI with suite runner and JSON export
- [x] LangGraph agent integration
- [x] Interactive React dashboard
- [x] FastAPI backend
- [ ] Run scenarios from the dashboard
- [ ] Domain expert chatbot for scenario creation
- [ ] Mind map visualization — interactive diagram of elicited processes and test types, built from the structured JSON
- [ ] GitHub Actions integration
- [ ] Event DAG support
- [ ] Multi-agent evaluation
- [ ] Fine-tuned domain expert chatbot (elicit fine-grained questions)
- [ ] MCP integration


## Contributing

This project is in early development. If you're interested in agent evaluation, CI/CD for AI, or collaborative tooling for technical and non-technical users, feel free to open an issue or reach out.

---

## License

TBD

---

## Acknowledgments

Architecture inspired by [ARE: Scaling Up Agent Environments and Evaluations](https://github.com/facebookresearch/meta-agents-research-environments) (Meta Superintelligence Labs, 2025).