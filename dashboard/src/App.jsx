import { useState, useEffect } from "react";


const checkTypes = ["tool", "arg", "result", "sequence", "content"];


function scenariosPassed({scenarios}) {
  return scenarios.filter(s => s.passed).length;
}

function checksPassed({scenarios}) {
  let passed = 0, total = 0;
  for (const s of scenarios) {
    for (const c of s.checks) {
      total++;
      if (c.passed) passed++;
    }
  }
  return [passed, total];
}

function capitalizeFirstLetter(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function rateByCheckType({scenarios, type}) {
  let passed = 0, total = 0;
  for (const s of scenarios) {
    for (const c of s.checks) {
      if (c.meta_type === type) {
        total++;
        if (c.passed) passed++;
      }
    }
  }
  return total > 0 ? Math.round(100 * passed / total) : 0;
}

// ––– Components –––––––––––––––––––––––––––––––––––––
 
function ListScenarios( { available, runStatus, results } ) {
  return (
  <div className="frame">
  <table className="scenario-list">
    <thead>
      <tr>
        <th>Name</th>
        <th>Description</th>
        <th>Number of checks</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {available.map((x) => (
        <tr key={x.id}>
          <td>{x.name}</td>
          <td>{x.description}</td>
          <td>{x.checks}</td>
          <td><StatusBadge scenarioId={x.id} runStatus={runStatus} results={results} /></td>
        </tr>
      ))}
      
    </tbody>
  </table>
  </div>);
}

function ProgressBar({ current, total }) {
  if (total === 0) return null;
  const pct = Math.round((current / total) * 100);
  return (
    <div className="progress-container">
      <div className="progress-label">
        <span>Running scenarios...</span>
        <span>{current}/{total} ({pct}%)</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function StatusBadge({ scenarioId, runStatus, results }) {
  const status = runStatus[scenarioId];
  if (!status) return null;
  if (status === "pending") return <span className="badge badge-pending">Pending</span>;
  if (status === "running") return <span className="badge badge-running">Running</span>;
  if (status === "error") return <span className="badge badge-error">Error</span>;
  // done — check pass/fail
  const result = results[scenarioId];
  if (result?.passed) return <span className="badge badge-done-pass">✅ Pass</span>;
  return <span className="badge badge-done-fail">❌ Fail</span>;
}


function SummaryTable({ scenarios, selectedId, onSelect }) {
  return (
    <table className="summary-table">
      <tbody>
        {scenarios.map((s, idx) => (
          <tr
            key={s.id}
            className={s.id === selectedId ? "selected" : ""}
            onClick={() => onSelect(s.id)}
          >
            <td>{idx + 1}/{scenarios.length}</td>
            <td>{s.name}</td>
            <td className={s.passed ? "status-pass" : "status-fail"}>
              {s.passed ? "✅ PASS" : "❌ FAIL"}
            </td>
            <td>{s.duration} s</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ScorePanel({scenarios}) {
  const [passed, total] = checksPassed({scenarios});
  const score = total > 0 ? Math.round((passed / total) * 100) : 0;
  const barClass = score === 100 ? "green" : score > 50 ? "yellow" : "red";
  
  return (
    <div className="score-panel">
      <div className="metric green">
        {scenariosPassed({scenarios})}/{scenarios.length} scenarios passed
      </div>
      <div className="metric green">
        {passed}/{total} checks
      </div>
      <div className="score-label">Score</div>
      <div className="score-bar-track">
        <div
          className={`score-bar-fill ${barClass}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <div className="score-value">{score}%</div>
    </div>
  );
}

function TypeTable({scenarios}) {

  return (<table className="type-table">
            <thead>
              <tr>
                <th>Check type</th>
                <th>Success rate</th>
              </tr>
            </thead>
            <tbody>
              {checkTypes.map((ct)=>
              <tr key={ct}>
                <th>
                  {ct}
                </th>
                <td>
                  {rateByCheckType({scenarios, type: ct})}%
                </td>
              </tr>)}
            </tbody>
          </table>)
}


function CheckSidebar({ scenario, selectedCheckId, onSelectCheck }) {
  return (
    <div>
      {checkTypes.map(ct => {
        const checks = scenario.checks.filter(c => c.meta_type === ct);
        if (checks.length === 0) return null;
        return (
          <div key={ct}>
            <div className="check-group-title">{capitalizeFirstLetter(ct)} check</div>
            {checks.map(c => (
              <button
                key={c.id}
                className={`check-item ${c.id === selectedCheckId ? "selected" : ""}`}
                onClick={() => onSelectCheck(c.id)}
              >
                <span className="check-name">{c.name}</span>
                <span className={`check-status ${c.passed ? "status-pass" : "status-fail"}`}>
                  {c.passed ? "Passed" : "Failed"}
                </span>
              </button>
            ))}
          </div>
        );
      })}
    </div>
  );
}

function CheckDetail({check}) {
    if (!check) return <div className="empty-state">Select a check to view details</div>;

    return <div className="check-detail">
      <h3>{check.name}</h3>
      <p className="check-description">{check.description}</p>
      <table className="result-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Actual</th>
            <th>Expected</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className={check.passed ? "status-pass" : "status-fail"}>
              {(check.passed)?"✅":"❌"}
            </td>
            <td  className={check.passed ? "actual-pass" : "actual-fail"}>{check.actual}</td>
            <td>{check.expected}</td>
          </tr>
        </tbody>
      </table>
    </div>;
}


export default function Dashboard() {
  
  const [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState([]);

  const [results, setResults] = useState(null);           // scenario_id → result
  const [runStatus, setRunStatus] = useState({});       // scenario_id → "pending" | "running" | "done"
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const [selectedScenario, setSelectedScenario] = useState(null);
  const [selectedCheck, setSelectedCheck] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/scenarios")
      .then(res => {return res.json()})
      .then(json => {setAvailable(json)})
  }, []);

  console.log(available.length)
  if (!results || loading) {
    return (
      <div className="dashboard">
        <h1>Agentflow</h1>
        <ListScenarios available={available} runStatus={runStatus} results={results} />
        {loading && <ProgressBar current={progress.current} total={progress.total} />}
        <button className="run-suite" onClick={runSuite} disabled={loading}>
          {loading ? "Running..." : "Run Suite"}
        </button>
      </div>
    );
  }

  async function runSuite() {
    setLoading(true);
    const total = available.length;
    setProgress({ current: 0, total });

    // Initialize all to pending
    const initialStatus = {};
    for (const s of available) initialStatus[s.id] = "pending";
    setRunStatus(initialStatus);
    setResults([]);
    
    for (let i = 0; i < available.length; i++) {
      const s = available[i];
      setRunStatus(prev => ({ ...prev, [s.id]: "running" }));

      try {
        const res = await fetch(`http://localhost:8000/scenarios/${s.id}`, { method: "POST" });
        const json = await res.json();
        setResults(prev => ([ ...prev, json ]));
        setRunStatus(prev => ({ ...prev, [s.id]: "done" }));
      } catch (err) {
        setRunStatus(prev => ({ ...prev, [s.id]: "error" }));
      }

      setProgress({ current: i + 1, total });
    }
    setLoading(false);
  }
  
  const scenarios = results;
  console.log(scenarios)
  
  const currentScenario = scenarios.find((x) => x.id === selectedScenario) || scenarios[0];
  console.log(currentScenario)
  const currentCheck = currentScenario.checks.find((x)=>x.id === selectedCheck) || currentScenario?.checks[0];

  function handleScenarioSelect(id) {
    setSelectedScenario(id);
    const scenario = scenarios.find(s => s.id === id);
    setSelectedCheck(scenario.checks[0]?.id || null);
  }

  const checkScore = checksPassed({scenarios});
  const score = Math.round((checkScore[0]/checkScore[1])*100);

  return (
    <div  className="dashboard">
      <h1>Agentflow</h1>
      <div className="frame">
        <h2 className="frame-title">Summary</h2>
        <SummaryTable 
        scenarios={scenarios} 
        selectedId={selectedScenario} 
        onSelect={setSelectedScenario}
        />
        <div className="bottom-summary" style={{display:'grid', gridTemplateColumns:"400px 1fr", gap:16}}>
          <TypeTable scenarios={scenarios}/>

          <ScorePanel scenarios={scenarios}/>
        </div>
      </div>
      <div className="frame">
          <h2 className="frame-title">Details: {currentScenario.name}</h2>
          <div className="details-grid">
            <CheckSidebar 
            scenario={currentScenario}
            selectedCheckId={selectedCheck}
            onSelectCheck={setSelectedCheck}
            />
            <CheckDetail check={currentCheck}/>
          </div>
          
      </div>

      <button className="run-suite" onClick={runSuite} disabled={loading}>
          {loading ? "Running..." : "Run Suite"}
        </button>
    </div>
  );
}