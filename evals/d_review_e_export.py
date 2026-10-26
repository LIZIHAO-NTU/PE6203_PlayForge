"""D independent controlled review of E's export instructions and immutable artifacts. Zero API."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkout',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
checkout=a.checkout.resolve();out=a.output.resolve()
if out.exists():raise ValueError('Choose a new output directory')
out.mkdir(parents=True)
sys.path.insert(0,str(checkout))
from agent.delivery import export_run
from agent import __version__
def hashes(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
source=out/'source';(source/'game').mkdir(parents=True);(source/'traces').mkdir()
(source/'game/index.html').write_text('<!doctype html><button>Controlled export fixture</button>',encoding='utf-8')
(source/'game/assets').mkdir();(source/'game/assets/plain.txt').write_text('Nested artifact bytes.\n',encoding='utf-8')
(source/'traces/events.jsonl').write_text('{"event":"controlled_fixture","private_note":"D_REVIEW_FAKE_PRIVATE_MARKER"}\n',encoding='utf-8')
(source/'summary.json').write_text('{"agent_version":"historical-fixture-version"}',encoding='utf-8')
(source/'.env').write_text('PRIVATE=D_REVIEW_FAKE_ENV_MARKER\n',encoding='utf-8')
before=hashes(source);dest=out/'export';manifest=export_run(source,dest)
after=hashes(source);readme=(dest/'README.md').read_text(encoding='utf-8')
checks={
 'source_unchanged':before==after,
 'game_bytes_match':hashes(source/'game')==hashes(dest/'game'),
 'trace_bytes_match':hashes(source/'traces')==hashes(dest/'traces'),
 'root_env_excluded':not (dest/'.env').exists(),
 'raw_trace_marker_preserved_as_documented':'D_REVIEW_FAKE_PRIVATE_MARKER' in (dest/'traces/events.jsonl').read_text(encoding='utf-8'),
 'historical_and_exporter_versions_distinguished':manifest['original_run_agent_version']=='historical-fixture-version' and manifest['agent_version']==__version__,
 'no_fabricated_report':not manifest['has_report'] and not (dest/'report.pdf').exists(),
 'course_acceptance_unclaimed':manifest['course_acceptance'] is None,
 'approved_requirement_not_included':not (dest/'SPECIFICATION.md').exists() and not (dest/'game_design_prompt.md').exists(),
 'explicit_requirement_command':'python -m agent SPECIFICATION.md' in readme,
 'explicit_supply_instruction':'supply your approved Markdown specification as SPECIFICATION.md' in readme,
 'old_unshipped_default_command_absent':'python -m agent game_design_prompt.md' not in readme,
 'both_readmes_match':readme==(dest/'agent/README.md').read_text(encoding='utf-8'),
}
rejects={}
for name,target in [('existing_output',dest),('inside_source',source/'nested')]:
 try:export_run(source,target);rejects[name]=False
 except ValueError:rejects[name]=True
checks['overwrite_and_nested_output_rejected']=all(rejects.values())
linked=out/'linked_source';(linked/'game').mkdir(parents=True);(linked/'traces').mkdir();(linked/'game/index.html').symlink_to(source/'game/index.html')
try:export_run(linked,out/'linked_export');checks['linked_artifact_rejected']=False
except ValueError:checks['linked_artifact_rejected']=not (out/'linked_export').exists()
# Inspect executable portability from the new export, without inheriting user provider settings.
env={k:v for k,v in os.environ.items() if not k.startswith(('LLM_','DEEPSEEK_','OPENAI_','OPENROUTER_')) and k!='PYTHONPATH'}
env['PYTHONUTF8']='1';cli=[]
for args in [['--help'],['export-run','--help']]:
 r=subprocess.run([sys.executable,'-X','utf8','-B','-m','agent',*args],cwd=dest,env=env,capture_output=True,text=True,timeout=30)
 cli.append({'args':args,'exit_code':r.returncode});assert r.returncode==0,r.stderr
checks['cli_loads_from_export_without_source_pythonpath']=all(x['exit_code']==0 for x in cli)
assert hashes(source)==before
report={'kind':'controlled_export_review_not_game_generation','model_api_calls':0,'browser_runs':0,'checks':checks,'cli':cli,'manifest':manifest,'source_file_hashes':before,
 'scope':'Synthetic source/export behavior and CLI loading only. No provider connectivity, teacher packaging approval or clean dependency install is claimed.',
 'privacy_note':'Fake marker demonstrates traces are copied verbatim; excluding root .env is not automatic trace redaction.'}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'checks':checks,'api_calls':0},indent=2))
