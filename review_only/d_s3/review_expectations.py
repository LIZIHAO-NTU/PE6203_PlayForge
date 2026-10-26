"""Finite static review of the preserved C v5 expectation snapshot; no game/API/browser."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from agent.contracts import validate_plan
h=lambda b:hashlib.sha256(b).hexdigest()
capsule=json.loads((ROOT/'original_evidence.json').read_text(encoding='utf-8'))
original={}
for name,entry in capsule['files'].items():
    raw=entry['text'].encode('utf-8')
    if h(raw)!=entry['sha256']:raise ValueError('Original evidence hash mismatch')
    original[name]=raw
spec=original['number_lock.txt'];plan=json.loads(original['number_lock.acceptance.json'])
pr=(ROOT/'number_lock.md').read_bytes()
assert h(spec)=='654d8e384b800d5ebd09b3905bd9d73a722c9e320a692194e23152bca2b43bf8'
assert h(original['number_lock.acceptance.json'])=='dc907ea38ebeef3bb4d93bc6b524304b0bd8c3934e88eca437a9899576c39a07'
assert spec.replace(b'\r\n',b'\n')==pr
assert json.loads((ROOT/'number_lock.acceptance.json').read_text(encoding='utf-8'))==plan
validate_plan(plan)
# Independently transcribed transition rules from the English requirement.
# Only these ten prescribed sequences are reviewed; this is not a game implementation.
rows=[];errors=[]
for t in plan['tests']:
 n=0;phase='Playing';feedback='Ready';field='';checks=[]
 steps=t.get('setup_steps',[])+t['steps']
 for i,s in enumerate(steps,1):
  action=s['action']
  if action=='fill':assert s['selector']=='#guess';field=s['text']
  elif action=='click':
   if s['selector']=='#restart':n=0;phase='Playing';feedback='Ready';field=''
   else:
    assert s['selector']=='#submit'
    if phase=='Playing':
     value=field.strip()
     if re.fullmatch('[1-9]',value) is None:feedback='Invalid input'
     else:
      n+=1
      if value=='7':phase='Won';feedback='Correct'
      elif n==3:phase='Lost';feedback='No attempts left'
      else:feedback='Too low' if int(value)<7 else 'Too high'
  elif action=='assert':
   assert s['op']=='eq'
   state={'attempts':n,'phase':phase,'feedback':feedback}
   if s['source']=='state':expected=state[s['path']]
   elif s['source']=='text':expected=str(state[s['selector'][1:]])
   else:assert s['source']=='value' and s['selector']=='#guess';expected=field
   ok=type(expected)==type(s['value']) and expected==s['value']
   record={'step':i,'source':s['source'],'field':s.get('selector',s.get('path')),'declared':s['value'],'independently_expected':expected,'matches':ok};checks.append(record)
   if not ok:errors.append({'test':t['id'],**record})
  else:raise ValueError('Unreviewed action '+action)
 rows.append({'test':t['id'],'setup_and_check_steps':len(steps),'assertions':len(checks),'state_assertions':sum(x['source']=='state' for x in checks),'checks':checks})
report={'kind':'static_review_not_game_execution','automated_scenarios':len(rows),
        'manual_checks':len(plan['manual_checks']),'assertion_expectations_reviewed':sum(x['assertions'] for x in rows),
        'state_assertions_reviewed':sum(x['state_assertions'] for x in rows),'errors':errors,'scenarios':rows,
        'api_calls':0,'browser_runs':0,'original_spec_sha256':h(spec),'public_spec_sha256':h(pr),
        'original_acceptance_sha256':h(original['number_lock.acceptance.json']),
        'public_acceptance_sha256':h((ROOT/'number_lock.acceptance.json').read_bytes())}
assert len(rows)==10 and report['assertion_expectations_reviewed']==79 and not errors
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
if args.output.exists():raise ValueError('Choose a new output file')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='scenarios'},indent=2))
