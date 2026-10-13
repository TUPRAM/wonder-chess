import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('asset_checks',ROOT/'tools/production/asset_checks.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class AssetChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.path=self.root/'mesh.obj'
        self.path.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 0 1\nf 1/1 2/2 3/3\n')
        self.manifest={'files':[m.fingerprint(self.path,self.root)]}
    def tearDown(self): self.temp.cleanup()
    def test_valid_source(self):
        r=m.source_preflight(self.root,{'manifest':self.manifest,'inspect':[{'path':'mesh.obj','maximum':{'triangles':2},'equals':{'triangles_missing_uv':0}}]})
        self.assertEqual(r['status'],'pass')
    def test_stale_hash(self):
        self.path.write_text(self.path.read_text()+'# changed\n')
        self.assertIn('Stale',m.verify_manifest(self.root,self.manifest)[0])
    def test_missing_file(self):
        self.path.unlink(); self.assertIn('Missing',m.verify_manifest(self.root,self.manifest)[0])
    def test_escape_rejected(self):
        with self.assertRaises(ValueError):m.confined(self.root,'../outside')
    def test_empty_manifest_rejected(self):self.assertTrue(m.verify_manifest(self.root,{}))
    def test_pointer_rejected(self):
        self.path.write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 999\n')
        self.assertTrue(m.verify_manifest(self.root,{'files':[m.fingerprint(self.path,self.root)]}))
    def test_invalid_triangle_indices(self):
        self.assertEqual(m.geometry_metrics([(0,0,0)],[(0,1,2)])['invalid_triangles'],1)
    def test_degenerate_detected(self):
        self.assertEqual(m.geometry_metrics([(0,0,0),(1,0,0),(2,0,0)],[(0,1,2)])['degenerate_triangles'],1)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):m.geometry_metrics([(float('nan'),0,0)],[(0,0,0)])
    def test_malformed_vertex_rejected(self):
        self.path.write_text('v 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
        r=m.source_preflight(self.root,{'manifest':{'files':[m.fingerprint(self.path,self.root)]},'inspect':[{'path':'mesh.obj'}]})
        self.assertEqual(r['status'],'fail')
    def test_missing_uv_rejected(self):
        self.path.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
        r=m.source_preflight(self.root,{'manifest':{'files':[m.fingerprint(self.path,self.root)]},'inspect':[{'path':'mesh.obj','equals':{'triangles_missing_uv':0}}]})
        self.assertEqual(r['status'],'fail')
    def test_wrong_budget(self):
        r=m.source_preflight(self.root,{'manifest':self.manifest,'inspect':[{'path':'mesh.obj','maximum':{'triangles':0}}]})
        self.assertEqual(r['status'],'fail')
    def test_unknown_budget_not_passed(self):
        r=m.source_preflight(self.root,{'manifest':self.manifest,'inspect':[{'path':'mesh.obj','maximum':{'triangles':None}}]})
        self.assertEqual(r['status'],'fail')
    def test_glb_embedded_triangle(self):
        blob=struct.pack('<9f',0,0,0,1,0,0,0,1,0)
        doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':36}], 'bufferViews':[{'buffer':0,'byteLength':36}],
             'accessors':[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3'}],
             'meshes':[{'primitives':[{'attributes':{'POSITION':0}}]}]}
        j=json.dumps(doc).encode(); j+=b' '*((-len(j))%4)
        raw=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob
        p=self.root/'a.glb';p.write_bytes(raw)
        self.assertEqual(m.inspect_glb(p)['triangles'],1)
    def test_bad_glb_header(self):
        p=self.root/'broken.glb';p.write_bytes(struct.pack('<III',0x46546c67,2,1000))
        with self.assertRaises(ValueError):m.inspect_glb(p)


if __name__=='__main__':unittest.main()
