"""Evaluation-only energy fixture. Never imported by autonomous generation."""
from agent.contracts import validate_plan

SPEC = ("Synthetic resource fixture. Offline vanilla HTML/CSS/JS. Energy starts at 5. "
        "Each successful click on #attack costs exactly 2 energy and increments attacks by 1. "
        "When energy is less than 2, attacks do nothing. #restart resets energy to 5 and "
        "attacks to 0. #energy and #attacks show bare integers. Include a visible "
        "[data-game-surface] and window.__gameTest.getState() returning actual "
        "{energy:number, attacks:number}. No timers, networking or tester-specific behavior.")


def resource_bundle(broken=False):
    cost = 1 if broken else 2
    return {"summary": "Evaluation-only resource fixture", "files": [{
        "path": "index.html", "content": '''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Energy</title>
<main data-game-surface style="width:320px;min-height:160px">
<h1>Energy</h1><span id="energy">5</span><span id="attacks">0</span>
<button id="attack">Attack</button><button id="restart">Restart</button></main>
<script>let energy=5,attacks=0;
function render(){document.querySelector('#energy').textContent=String(energy);
document.querySelector('#attacks').textContent=String(attacks)}
document.querySelector('#attack').onclick=()=>{if(energy>=2){energy-=''' + str(cost) + ''';attacks++;render()}};
document.querySelector('#restart').onclick=()=>{energy=5;attacks=0;render()};
window.__gameTest={getState:()=>({energy,attacks})};</script></html>'''}]}


def resource_plan(conflict=False):
    def click(selector):
        return {"action": "click", "selector": selector}
    def check(key, value, source="state"):
        return {"action": "assert", "source": source, "op": "eq", "value": value,
                **({"path": key} if source == "state" else {"selector": "#" + key})}
    return validate_plan({"supported": True, "title": "Frozen resource checks",
        "development_plan": ["Check energy, legal actions and restart"],
        "state_contract": {"energy": "number", "attacks": "number"},
        "requirements": [
            {"id": "R1", "text": "Start with 5 energy; attack costs 2", "verification": "automated"},
            {"id": "R2", "text": "Insufficient energy cannot attack", "verification": "automated"},
            {"id": "R3", "text": "Restart resets energy and attacks", "verification": "automated"}],
        "tests": [
            {"id": "T1", "description": "First attack", "requirement_ids": ["R1"],
             "steps": [check("energy", 5), click("#attack"), check("energy", 2 if conflict else 3),
                       check("energy", "3", "text"), check("attacks", 1)]},
            {"id": "T2", "description": "Repeated attacks, rejected action, restart",
             "requirement_ids": ["R1", "R2", "R3"], "steps": [
                 click("#attack"), click("#attack"), check("energy", 1), check("attacks", 2),
                 click("#attack"), check("energy", 1), check("attacks", 2),
                 check("energy", "1", "text"), check("attacks", "2", "text"),
                 click("#restart"), check("energy", 5), check("attacks", 0),
                 check("energy", "5", "text"), check("attacks", "0", "text")]}],
        "manual_checks": []})


def resource_state_plan(conflict=False):
    """A second frozen-test fault: incompatible energy snapshots without an action."""
    plan = resource_plan(conflict=conflict)
    if conflict:
        steps = plan["tests"][0]["steps"]
        steps.insert(3, {"action": "assert", "source": "state", "path": "attacks",
                         "op": "eq", "value": 1})
        steps.insert(4, {"action": "assert", "source": "state", "path": "energy",
                         "op": "eq", "value": 3})
    return validate_plan(plan)
