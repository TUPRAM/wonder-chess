import copy, hashlib, json, pathlib, sys
out=pathlib.Path(sys.argv[1]); root=pathlib.Path.cwd(); staged=root/'game/Content/WonderChess/SourceData'
old_units=json.loads((staged/'units.json').read_text(encoding='utf-8'))
new_units=json.loads((root/'data/units.json').read_text(encoding='utf-8'))
old_rules=json.loads((staged/'rules.alpha.json').read_text(encoding='utf-8'))
new_rules=json.loads((root/'data/rules.alpha.json').read_text(encoding='utf-8'))
normalized_units=copy.deepcopy(new_units)
for before,after in zip(old_units['units'], normalized_units['units']):
    if before['id']=='wc_u_dragonkin_rogue':
        after['art']['risk']=before['art']['risk']
        after['tactics']['contrast']=before['tactics']['contrast']
normalized_rules=copy.deepcopy(new_rules); normalized_rules['network']['protocol_version']=old_rules['network']['protocol_version']
assert normalized_units==old_units, 'Unexpected units change'
assert normalized_rules==old_rules, 'Unexpected rules change'
result={'status':'PASS_CANONICAL_CHANGE_SCOPE_ONLY','old_protocol':old_rules['network']['protocol_version'],'new_protocol':new_rules['network']['protocol_version'],'balance_version':new_rules['balance_version'],'all_other_rules_and_unit_fields_identical':True,'unit_narrative_changes':['wc_u_dragonkin_rogue.art.risk','wc_u_dragonkin_rogue.tactics.contrast'],'catalog_digest':json.loads((root/'generated/catalog_digest.json').read_text())['combined_sha256'],'inputs':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'data/units.json',root/'data/rules.alpha.json',staged/'units.json',staged/'rules.alpha.json']},'boundary':'Protocol/source amendment only; new native and packaged execution still required. Prior export hashes retain historical canonical snapshots.'}
(out/'scope-parity.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))

