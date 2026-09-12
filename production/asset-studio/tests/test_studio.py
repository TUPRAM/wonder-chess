"""Synthetic fixtures only. No real asset/Blender/human review is performed here."""
from pathlib import Path
import ast,base64,importlib.util,json,os,sys,tempfile,unittest,wave
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/asset_studio'))
from assetctl import Studio,GateError,initialize,load,write_new,relative_path,locked,encoded
from image_review import crop_pack,contact_sheet,mask_metrics
from run_blender import build_command
from PIL import Image

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'asset'
        initialize(self.root,'wc_test_guardian','hero','Synthetic fixture');self.s=Studio(self.root)
    def tearDown(self):self.temp.cleanup()
    def report(self,stage):
        r=self.s.report_template(stage);r['author']='synthetic-author';r['method']='Synthetic test data only, not a real production observation.'
        folder=self.root/'stages'/stage;folder.mkdir(parents=True,exist_ok=True)
        source=folder/'source.txt';source.write_text('synthetic source '+stage)
        image=folder/'image.png';Image.new('RGB',(32,32)).save(image)
        audio=folder/'audio.wav'
        with wave.open(str(audio),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000);f.writeframes(b'\x00\x00'*8)
        r['artifacts']=[{'path':p.relative_to(self.root).as_posix(),'category':kind} for p,kind in [(source,'source'),(image,'image'),(audio,'audio')]]
        for c in r['checks']:c.update(status='pass',notes='Synthetic fixture for schema/ledger test.',evidence=[r['artifacts'][0]['path']])
        path='reports/'+stage+'.json';(self.root/path).write_bytes(encoded(r));return path,r
    def accept(self,stage):
        path,_=self.report(stage);c=self.s.prepare(path)
        return self.s.approve(c,'synthetic-reviewer',self.s.gates[stage]['role'],'Synthetic test signoff, not actual human approval.',True)
    def test_new_workspace_pending(self):self.assertTrue(all(x['status']=='pending' for x in self.s.status()))
    def test_init_refuses_nonempty(self):
        with self.assertRaises(GateError):initialize(self.root,'wc_test_guardian','hero','Again')
    def test_invalid_id(self):
        with self.assertRaises(GateError):initialize(Path(self.temp.name)/'bad','../escape','hero','Bad')
    def test_invalid_kind(self):
        with self.assertRaises(GateError):initialize(Path(self.temp.name)/'bad','wc_ok','banana','Bad')
    def test_inapplicable_stage(self):
        with self.assertRaises(GateError):self.s.report_template('not_a_stage')
    def test_template_unexecuted(self):self.assertTrue(all(x['status']=='not_run' for x in self.s.report_template('forms')['checks']))
    def test_unexecuted_cannot_prepare(self):
        p,r=self.report('brief');r['checks'][0]['status']='not_run';(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_failed_check_blocks(self):
        p,r=self.report('brief');r['checks'][0]['status']='fail';(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_missing_check_blocks(self):
        p,r=self.report('brief');r['checks'].pop();(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_duplicate_check_blocks(self):
        p,r=self.report('brief');r['checks'][-1]=r['checks'][0];(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_blank_observation_blocks(self):
        p,r=self.report('brief');r['checks'][0]['notes']='';(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_missing_source_blocks(self):
        p,r=self.report('brief');r['artifacts']=[a for a in r['artifacts'] if a['category']!='source'];(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_missing_artifact_blocks(self):
        p,r=self.report('brief');(self.root/r['artifacts'][0]['path']).unlink()
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_unlisted_evidence_blocks(self):
        p,r=self.report('brief');r['checks'][0]['evidence']=['phantom.png'];(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_major_defect_blocks(self):
        p,r=self.report('brief');r['defects']=[{'severity':'major','status':'open'}];(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_major_cannot_be_minor_exception(self):
        p,r=self.report('brief');r['defects']=[{'severity':'major','status':'accepted_minor','reason':'Bad waiver'}];(self.root/p).write_bytes(encoded(r))
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_explicit_minor_exception(self):
        import jsonschema
        p,r=self.report('brief');r['defects']=[{'severity':'minor','status':'accepted_minor','reason':'Synthetic scoped test only.','affected_use':'Synthetic fixture only.','owner':'synthetic-author','later_action':'Resolve before the next fixture revision.'}];(self.root/p).write_bytes(encoded(r))
        jsonschema.validate(r,load(ROOT/'schemas/review_report.schema.json'))
        self.assertTrue(self.s.prepare(p).endswith('.json'))
    def test_minor_exception_requires_complete_disposition(self):
        import jsonschema
        complete={'severity':'minor','status':'accepted_minor','reason':'Synthetic scoped test only.','affected_use':'Synthetic fixture only.','owner':'synthetic-author','later_action':'Resolve before the next fixture revision.'}
        for field in ('reason','affected_use','owner','later_action'):
            for invalid in (None,'', '  ',42):
                with self.subTest(field=field,value=invalid):
                    p,r=self.report('brief');d=dict(complete);d[field]=invalid;r['defects']=[d];(self.root/p).write_bytes(encoded(r))
                    with self.assertRaises(GateError):self.s.prepare(p)
                    with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(r,load(ROOT/'schemas/review_report.schema.json'))
    def test_upstream_required(self):
        p,_=self.report('references')
        with self.assertRaises(GateError):self.s.prepare(p)
    def test_prepare_is_not_approval(self):
        p,_=self.report('brief');self.s.prepare(p)
        self.assertEqual(self.s.status()[0]['status'],'pending')
    def test_ack_required(self):
        p,_=self.report('brief');c=self.s.prepare(p)
        with self.assertRaises(GateError):self.s.approve(c,'reviewer','technical_reviewer','Note',False)
    def test_author_cannot_self_technical_review(self):
        p,_=self.report('brief');c=self.s.prepare(p)
        with self.assertRaises(GateError):self.s.approve(c,'synthetic-author','technical_reviewer','Note',True)
    def test_role_enforced(self):
        self.accept('brief');p,_=self.report('references');c=self.s.prepare(p)
        with self.assertRaises(GateError):self.s.approve(c,'agent','technical_reviewer','Note',True)
    def test_human_declaration_not_authenticated(self):
        self.accept('brief');rel=self.accept('references');r=load(self.root/rel)
        self.assertFalse(r['signoff']['identity_authenticated'])
    def test_evidence_change_invalidates(self):
        self.accept('brief');(self.root/'stages/brief/source.txt').write_text('different')
        self.assertEqual(self.s.status()[0]['status'],'stale_or_invalid')
    def test_report_change_invalidates(self):
        self.accept('brief');p=self.root/'reports/brief.json';r=load(p);r['method']='A changed report after approval.';p.write_bytes(encoded(r))
        self.assertEqual(self.s.status()[0]['status'],'stale_or_invalid')
    def test_downstream_invalidated(self):
        self.accept('brief');self.accept('references');(self.root/'stages/brief/source.txt').write_text('changed')
        self.assertEqual(self.s.status()[1]['status'],'stale_or_invalid')
    def test_manifest_change_detected_in_long_lived_instance(self):
        self.accept('brief');p=self.root/'asset.json';m=load(p);m['design_revision']='r2';p.write_bytes(encoded(m))
        self.assertEqual(self.s.status()[0]['status'],'stale_or_invalid')
    def test_changed_before_approval_rejected(self):
        p,_=self.report('brief');c=self.s.prepare(p);(self.root/'stages/brief/source.txt').write_text('changed')
        with self.assertRaises(GateError):self.s.approve(c,'reviewer','technical_reviewer','Note',True)
    def test_path_escape(self):
        with self.assertRaises(GateError):relative_path(self.root,'../outside',False)
    def test_absolute_path(self):
        with self.assertRaises(GateError):relative_path(self.root,'/tmp/outside',False)
    def test_drive_path(self):
        with self.assertRaises(GateError):relative_path(self.root,'C:/outside',False)
    def test_symlink_escape(self):
        target=Path(self.temp.name)/'outside.txt';target.write_text('outside')
        try:(self.root/'link').symlink_to(target)
        except OSError:self.skipTest('Symlink unavailable')
        with self.assertRaises(GateError):relative_path(self.root,'link')
    def test_lock_exclusive(self):
        with locked(self.root):
            with self.assertRaises(GateError):
                with locked(self.root):pass
        self.assertFalse((self.root/'.assetctl.lock').exists())
    def test_refuse_overwrite(self):
        with self.assertRaises(GateError):write_new(self.root/'asset.json',{})
    def test_every_asset_route_synthetic_flow(self):
        rules=load(ROOT/'config/routes.json')
        for kind in rules['routes']:
            with self.subTest(kind=kind):
                self.root=Path(self.temp.name)/kind;initialize(self.root,'wc_test_'+kind,kind,'Synthetic '+kind);self.s=Studio(self.root)
                for stage in self.s.gates:self.accept(stage)
                self.assertTrue(all(x['status']=='accepted_current' for x in self.s.status()))

class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name);self.im=self.r/'input.png';Image.new('RGB',(20,30),(70,80,90)).save(self.im)
    def tearDown(self):self.temp.cleanup()
    def plan(self,box):
        p=self.r/'boxes.json';p.write_text(json.dumps({'crops':[{'id':'face','box_xyxy':box}]}));return p
    def test_native_crop(self):
        r=crop_pack(self.im,self.plan([2,3,10,15]),self.r/'crop')
        with Image.open(self.r/'crop/face.png') as im:self.assertEqual(im.size,(8,12))
        self.assertFalse(r['crops'][0]['resampled'])
    def test_out_of_bounds(self):
        with self.assertRaises(ValueError):crop_pack(self.im,self.plan([0,0,50,50]),self.r/'crop')
    def test_no_crop_overwrite(self):
        p=self.plan([0,0,5,5]);crop_pack(self.im,p,self.r/'crop')
        with self.assertRaises(ValueError):crop_pack(self.im,p,self.r/'crop')
    def test_sheet(self):
        r=contact_sheet([self.im,self.im],self.r/'sheet.png',100);self.assertIsNone(r['quality_score'])
        with Image.open(self.r/'sheet.png') as im:self.assertEqual(im.size,(200,146))
    def test_registration_required(self):
        with self.assertRaises(ValueError):mask_metrics(self.im,self.im,False)
    def test_mask_identity(self):
        white=self.r/'white.png';Image.new('L',(20,30),255).save(white)
        self.assertEqual(mask_metrics(white,white,True)['intersection_over_union'],1)
    def test_empty_mask_rejected(self):
        black=self.r/'black.png';Image.new('L',(20,30),0).save(black)
        with self.assertRaises(ValueError):mask_metrics(black,black,True)
    def test_no_auto_resize(self):
        different=self.r/'different.png';Image.new('L',(21,30),255).save(different)
        with self.assertRaises(ValueError):mask_metrics(self.im,different,True)

class PackageTests(unittest.TestCase):
    def test_python_syntax(self):
        paths=list((ROOT/'tools').rglob('*.py'))
        self.assertEqual(len(paths),6)
        for p in paths:
            with self.subTest(file=p.name):ast.parse(p.read_text())
    def test_skill_inventory(self):
        rows=load(ROOT/'config/skill_catalog.json');self.assertEqual(len(rows),22);self.assertEqual(len({x['name'] for x in rows}),22)
        for row in rows:
            p=ROOT/'.agents/skills'/row['name']/'SKILL.md';text=p.read_text()
            self.assertTrue(text.startswith('---\nname: '+row['name']))
            self.assertTrue((ROOT/row['manual']).is_file())
            for section in ['## Inputs and scope','## Procedure','## Outputs and exit','## Failure and rollback']:self.assertIn(section,text)
    def test_routes_topological_order(self):
        for kind,r in load(ROOT/'config/routes.json')['routes'].items():
            seen=set()
            for stage,g in r['gates'].items():
                self.assertTrue(set(g['deps']).issubset(seen),(kind,stage));seen.add(stage)
            self.assertEqual(r['gates']['release']['role'],'human')
    def test_json_valid(self):
        for p in ROOT.rglob('*.json'):
            with self.subTest(file=str(p.relative_to(ROOT))):load(p)
    def test_manifest_schema(self):
        import jsonschema
        jsonschema.validate(load(ROOT/'templates/asset_manifest.json'),load(ROOT/'schemas/asset_manifest.schema.json'))
    def test_report_template_schema(self):
        import jsonschema
        with tempfile.TemporaryDirectory() as d:
            initialize(Path(d),'wc_test_hero','hero','Synthetic fixture')
            jsonschema.validate(Studio(Path(d)).report_template('brief'),load(ROOT/'schemas/review_report.schema.json'))
    def test_blender_runner_rejects_missing_source(self):
        with self.assertRaises(ValueError):build_command('blender',ROOT/'absent.blend','scene_audit',[])
    def test_blender_runner_allowlist(self):
        with self.assertRaises(ValueError):build_command('blender',ROOT/'absent.blend','arbitrary_remote_script',[])
    def test_blender_command_no_shell_and_autoexec_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source with space.blend';p.write_bytes(b'SYNTHETIC_NOT_BLEND')
            cmd=build_command(sys.executable,p,'scene_audit',['--collection','TEST'])
            self.assertIsInstance(cmd,list);self.assertIn('--disable-autoexec',cmd);self.assertIn('--python-exit-code',cmd);self.assertIn(str(p.resolve()),cmd)
            self.assertLess(cmd.index('--factory-startup'),cmd.index(str(p.resolve())))

if __name__=='__main__':unittest.main()
