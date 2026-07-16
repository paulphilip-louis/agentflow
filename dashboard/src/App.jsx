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
  const [data, setData] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [selectedCheck, setSelectedCheck] = useState(null);


  useEffect(() => {
    fetch("/results.json")
      .then(res => {
        console.log("Status:", res.status);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(json => {
        console.log("Loaded:", json);
        setData(json);
      })
      .catch(err => console.error("Fetch failed:", err));
  }, []);

  if (!data) return <p>Loading...</p>;
  
  const scenarios = data.results;
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
    </div>
  );
}