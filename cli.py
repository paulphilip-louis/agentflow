#!/usr/bin/env python3
"""
agentflow CLI — run evaluation scenarios against agents.

Usage:
    python -m agentflow run --scenario path/to/scenario.yaml
    python -m agentflow run --suite path/to/scenarios/ --output results.json
    python -m agentflow list --suite path/to/scenarios/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

# ─── ANSI color helpers ──────────────────────────────────────────────

class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[38;5;114m"
    RED     = "\033[38;5;203m"
    YELLOW  = "\033[38;5;221m"
    BLUE    = "\033[38;5;111m"
    CYAN    = "\033[38;5;117m"
    GRAY    = "\033[38;5;245m"
    WHITE   = "\033[38;5;255m"
    BG_DARK = "\033[48;5;235m"

def colored(text, color):
    return f"{color}{text}{Colors.RESET}"

def bold(text):
    return f"{Colors.BOLD}{text}{Colors.RESET}"


# ─── Output formatting ───────────────────────────────────────────────

LOGO = r"""
   ___                __  __ __              
  / _ |___ ____ ___  / /_/ _/ /___ __  __
 / __ / _ `/ -_) _ \/ __/ _/ / _ \  |/| /
/_/ |_\_, /\__/_//_/\__/_//_/\___/__,__/  
     /___/                            v0.1.0
"""

def print_header():
    print(colored(LOGO, Colors.CYAN))
    print(colored("─" * 56, Colors.GRAY))
    print()


def print_scenario_info(scenario):
    print(f"  {colored('Scenario', Colors.BLUE)}  {bold(scenario.config.name)}")
    print(f"  {colored('Desc', Colors.GRAY)}      {scenario.config.description}")
    apps_str = ", ".join(scenario.apps.keys())
    print(f"  {colored('Apps', Colors.GRAY)}      {apps_str}")
    n_events = len(scenario.events)
    n_checks = len(scenario.verifier.checks)
    print(f"  {colored('Events', Colors.GRAY)}    {n_events} scheduled")
    print(f"  {colored('Checks', Colors.GRAY)}    {n_checks} verifications")
    print()
    print(colored("─" * 56, Colors.GRAY))
    print()


def print_execution_trace(event_log):
    """Print a compact timeline of all events."""
    print(f"  {bold('Execution Trace')}")
    print()
    
    events = event_log.to_list()
    for i, event in enumerate(events):
        t = event.timestamp if event.timestamp is not None else "?"
        
        # Determine event type and icon
        class_name = event.__class__.__name__
        if class_name == "UserEvent":
            icon = "💬"
            label = colored("USER ", Colors.YELLOW)
            msg = event.message[:60] + "..." if len(event.message) > 60 else event.message
            detail = colored(f'"{msg}"', Colors.WHITE)
        elif class_name == "AgentEvent":
            icon = "🤖"
            label = colored("AGENT", Colors.CYAN)
            status_color = Colors.GREEN if event.status.name == "COMPLETED" else Colors.RED
            status_icon = colored("✓", status_color) if event.status.name == "COMPLETED" else colored("✗", status_color)
            detail = f"{colored(event.app, Colors.GRAY)}.{colored(event.tool, Colors.WHITE)}({colored(str(event.args), Colors.DIM)}) {status_icon}"
        elif class_name == "EnvEvent":
            icon = "🌐"
            label = colored("ENV  ", Colors.BLUE)
            msg = event.message[:60] + "..." if len(event.message) > 60 else event.message
            detail = f"{colored(event.app, Colors.GRAY)}/{event.event_type}: {msg}"
        else:
            icon = "❓"
            label = "???"
            detail = str(event)
        
        t_str = colored(f"t={str(t):>4}", Colors.DIM)
        connector = colored("│", Colors.GRAY)
        
        print(f"  {connector}  {t_str}  {icon} {label}  {detail}")
    
    print(f"  {colored('│', Colors.GRAY)}")
    print()


def print_verification_result(result):
    """Print check results with pass/fail indicators."""
    print(f"  {bold('Verification')}")
    print()
    
    for r in result.results:
        if r.passed:
            icon = colored("  ✅ PASS ", Colors.GREEN)
        else:
            icon = colored("  ❌ FAIL ", Colors.RED)
        
        name = colored(r.name, Colors.WHITE)
        print(f"  {icon}  {name}")
        
        if not r.passed:
            # Show detail for failures
            detail_lines = r.detail.split(", ")
            for line in detail_lines:
                print(f"           {colored(line.strip(), Colors.DIM)}")
    
    print()
    print(colored("─" * 56, Colors.GRAY))
    
    # Summary
    passed = sum(1 for r in result.results if r.passed)
    total = len(result.results)
    pct = (passed / total * 100) if total > 0 else 0
    
    if result.passed:
        status = colored("ALL PASSED", Colors.GREEN)
        bar_color = Colors.GREEN
    else:
        status = colored("FAILED", Colors.RED)
        bar_color = Colors.RED
    
    # Score bar
    bar_width = 30
    filled = int(bar_width * pct / 100)
    bar = colored("█" * filled, bar_color) + colored("░" * (bar_width - filled), Colors.GRAY)
    
    print()
    print(f"  {bold('Result')}  {status}  {passed}/{total} checks")
    print(f"  {bold('Score')}   {bar}  {pct:.0f}%")
    print()


def return_json_summary(scenario, scenario_id, result, duration):
    """Return a JSON-serializable dict of the run."""
    return {
        "id": scenario_id,
        "name": scenario.config.name,
        "description": scenario.config.description,
        "duration": round(duration, 3),
        "passed": result.passed,
        "score": round(result.score, 4),
        "checks": [
            {
                "id": str(uuid4()),
                "name": r.name,
                "meta_type": r.meta_type,
                "passed": r.passed,
                "expected": r.expected,
                "actual": r.actual
            }
            for r in result.results
        ]
    }


# ─── CLI commands ─────────────────────────────────────────────────────

def run_single_scenario(scenario_path, output_path=None, verbose=True):
    """Run a single scenario and print results."""
    # Import here to avoid circular deps — adjust paths to your project
    from runtime.core.scenario import Scenario
    from runtime.core.runner import Runner
    
    scenario = Scenario(scenario_path)
    runner = Runner(verifier=scenario.verifier)
    
    if verbose:
        print_header()
        print_scenario_info(scenario)
        print(f"  {colored('Running...', Colors.YELLOW)}")
        print()
    
    start = time.time()
    result = runner.run(scenario)
    duration = time.time() - start
    
    if verbose:
        print_execution_trace(runner.env.eventLog)  # requires storing env on runner
        print_verification_result(result)
        print(f"  {colored('Duration', Colors.GRAY)}  {duration:.2f}s")
        print()
    
    scenario_id = scenario_path.split('/')[-1].split(".yaml")[0]
    summary = return_json_summary(scenario, scenario_id, result, duration)
    
    if output_path:
        PUBLIC_FOLDER = "dashboard/public"
        with open(os.path.join(PUBLIC_FOLDER, output_path), "w") as f:
            json.dump(summary, f, indent=2)
        if verbose:
            print(f"  {colored('Saved', Colors.GRAY)}    {output_path}")
            print()
    
    return summary


def run_suite(suite_path, output_path=None):
    """Run all .yaml scenarios in a directory."""
    suite_dir = Path(suite_path)
    scenarios = sorted(suite_dir.glob("*.yaml"))
    
    if not scenarios:
        print(colored(f"  No .yaml files found in {suite_path}", Colors.RED))
        return
    
    print_header()
    print(f"  {bold('Suite')}  {suite_dir.name}")
    print(f"  {colored('Scenarios', Colors.GRAY)}  {len(scenarios)} found")
    print()
    print(colored("─" * 56, Colors.GRAY))
    print()
    
    all_results = []
    total_passed = 0
    total_checks = 0
    
    for i, path in enumerate(scenarios, 1):
        print(f"  {colored(f'[{i}/{len(scenarios)}]', Colors.DIM)} {bold(path.stem)}", end="  ")
        
        try:
            summary = run_single_scenario(str(path), verbose=False)
            all_results.append(summary)
            
            n_passed = sum(1 for c in summary["checks"] if c["passed"])
            n_total = len(summary["checks"])
            total_passed += n_passed
            total_checks += n_total
            
            if summary["passed"]:
                print(colored("✅ PASS", Colors.GREEN), end="  ")
            else:
                print(colored("❌ FAIL", Colors.RED), end="  ")
            
            print(colored(f"{n_passed}/{n_total}  {summary['duration']:.2f}s", Colors.DIM))
            
        except Exception as e:
            print(colored(f"💥 ERROR: {e}", Colors.RED))
            all_results.append({"scenario": path.stem, "passed": False, "error": str(e)})
    
    # Suite summary
    print()
    print(colored("─" * 56, Colors.GRAY))
    
    suite_passed = sum(1 for r in all_results if r.get("passed"))
    suite_total = len(all_results)
    pct = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    bar_width = 30
    filled = int(bar_width * pct / 100)
    bar_color = Colors.GREEN if suite_passed == suite_total else Colors.YELLOW if pct > 50 else Colors.RED
    bar = colored("█" * filled, bar_color) + colored("░" * (bar_width - filled), Colors.GRAY)
    
    print()
    print(f"  {bold('Suite Result')}  {suite_passed}/{suite_total} scenarios passed")
    print(f"  {bold('Checks')}       {total_passed}/{total_checks} total checks")
    print(f"  {bold('Score')}        {bar}  {pct:.0f}%")
    print()
    
    if output_path:
        with open(output_path, "w") as f:
            json.dump({"suite": suite_dir.name, "results": all_results}, f, indent=2)
        print(f"  {colored('Saved', Colors.GRAY)}  {output_path}")
        print()


def list_scenarios(suite_path):
    """List available scenarios in a directory."""
    suite_dir = Path(suite_path)
    scenarios = sorted(suite_dir.glob("*.yaml"))
    
    print_header()
    print(f"  {bold('Available Scenarios')}  {suite_dir}")
    print()
    
    import yaml
    for path in scenarios:
        with open(path) as f:
            raw = yaml.safe_load(f)
        name = raw.get("name", path.stem)
        desc = raw.get("description", "")[:60]
        n_checks = len(raw.get("verifier", {}).get("checks", []))
        
        print(f"  {colored('●', Colors.CYAN)}  {bold(name)}")
        print(f"     {colored(desc, Colors.DIM)}")
        print(f"     {colored(f'{n_checks} checks', Colors.GRAY)}  {colored(str(path), Colors.DIM)}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="agentflow",
        description="Run evaluation scenarios for AI agents",
    )
    sub = parser.add_subparsers(dest="command")
    
    # run command
    run_parser = sub.add_parser("run", help="Run scenario(s)")
    run_parser.add_argument("--scenario", "-s", type=str, help="Path to a single .yaml scenario")
    run_parser.add_argument("--suite", type=str, help="Path to a directory of .yaml scenarios")
    run_parser.add_argument("--output", "-o", type=str, help="Save results to JSON file")
    
    # list command
    list_parser = sub.add_parser("list", help="List available scenarios")
    list_parser.add_argument("--suite", type=str, required=True, help="Path to scenarios directory")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    
    
    if args.command == "run":
        if args.scenario:
            run_single_scenario(args.scenario, output_path=args.output)
        elif args.suite:
            run_suite(args.suite, output_path=args.output)
        else:
            run_parser.print_help()
    
    elif args.command == "list":
        list_scenarios(args.suite)


if __name__ == "__main__":
    main()
