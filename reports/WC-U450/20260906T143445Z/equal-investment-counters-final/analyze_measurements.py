from pathlib import Path
import csv,json,hashlib,collections
p=Path('reports/WC-U450/20260906T143445Z/equal-investment-counters-final')
read=lambda name:list(csv.DictReader((p/name).open(newline='',encoding='utf-8')))
out=read('outcomes.csv');units=read('unit-outcomes.csv');events=read('events.csv');deploy=read('deployments.csv')
summary=json.loads((p/'summary.json').read_text());process=json.loads((p/'process.json').read_text(encoding='utf-8-sig'))
assert len(out)==192 and len(units)==len(deploy)==2304 and len(events)==summary['events']==42594
assert summary['assertions']==352876 and '352876 assertions' in (p/'run.log').read_text()
assert process['status']=='PASS_EXECUTION_ONLY' and process['compile_exit']==process['process_exit']==0 and not process['inputs_changed_during_run']
for name,expected in process['output_sha256'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==expected,name
lookup={r['fight']:r for r in out};deployed=collections.defaultdict(list)
for row in deploy:deployed[row['fight'],row['side']].append(row)
for key,rows in deployed.items():
    result=lookup[key[0]]
    assert len(rows)==6 and len({r['unit_id'] for r in rows})==6
    assert sum(int(r['purchase_gold']) for r in rows)==int(result['purchase_gold_each'])
    assert sum(int(r['copies']) for r in rows)==int(result['copies_each'])
    assert {r['star'] for r in rows}=={result['star']}
    assert len({(r['local_col'],r['local_row']) for r in rows})==6
pooled={};detail={};focus_instances={}
for row in units:
    if row['focus']=='1':focus_instances[row['fight'],row['instance']]=row
for row in out:
    key=row['subject']+' / '+row['pressure']
    record=pooled.setdefault(key,dict(runs=0,wins=0,losses=0,draws=0,timeouts=0,side0_wins=0,side1_wins=0))
    record['runs']+=1;record['wins']+=int(row['subject_result'])==1;record['losses']+=int(row['subject_result'])==-1
    record['draws']+=int(row['subject_result'])==0;record['timeouts']+=int(row['timeout'])
    record['side'+row['subject_side']+'_wins']+=int(row['subject_result'])==1
for event in events:
    identity=(event['fight'],event['source'])
    if identity not in focus_instances:continue
    match=lookup[event['fight']];key=match['subject']+' / star'+match['star']
    record=detail.setdefault(key,dict(focus_effect_counts=collections.Counter(),focus_positive_rate_packet_bp=collections.Counter(),focus_applied_stun_packet_ms=0))
    record['focus_effect_counts'][event['effect']]+=1
    if event['effect']=='attack_rate_modifier' and int(event['resolved'])>0:record['focus_positive_rate_packet_bp'][event['resolved']]+=1
    if event['effect']=='stun':record['focus_applied_stun_packet_ms']+=int(event['resolved'])
report={'status':'VERIFIED_COUNTER_MEASUREMENT_NOT_BALANCE_ACCEPTANCE','source_run':str(p),'actual_combats':192,'assertions':352876,'events':42594,'timeouts':27,'pooled_by_subject_pressure':pooled,'focus_event_details_by_star':detail,
'checks':['All current output hashes match process manifest','Every192 fight has6 distinct heroes and equal cost/copy budget on both sides','2304 unit summaries and deployments match192 twelve-unit fights','Console and summary assertion totals agree'],
'limitations':['Fixed curated deployments, not optimized best responses or individual hero ablation','Four initiative seeds and both board sides;192 fights include correlated two-star repeats','Equal gold/copies exclude acquisition rarity, shop rolls, XP and preparation opportunity','Active action totals count actions with resolved events, not all commitments','Stun packet durations overlap; actual target uptime is separate in unit-outcomes.csv','No game frame-time, graphical, audio, human or physical-LAN evidence'],
'input_digest':summary['content_digest'],'process_sha256':hashlib.sha256((p/'process.json').read_bytes()).hexdigest()}
(p/'counter-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
