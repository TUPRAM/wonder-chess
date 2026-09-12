"""Synthetic tests; none execute Blender or validate Ada's actual grip."""
import copy
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import contact_math as c

L = dict(wrist=(0,0,0), middle_mcp=(0,.08,0), index_mcp=(.025,.075,0),
         little_mcp=(-.025,.065,0), middle_tip=(0,.16,0), palmar_point=(0,.04,.01))
I = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
T = [[0,-1,0,.7],[1,0,0,-.3],[0,0,1,1.2],[0,0,0,1]]

class ContactTests(unittest.TestCase):
    def assertVector(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=9)
    def test_distal(self): self.assertVector(c.hand_frame(**L).y_distal,(0,1,0))
    def test_palmar(self): self.assertVector(c.hand_frame(**L).z_palmar,(0,0,1))
    def test_proper_rotation(self): c.validate_rigid(c.hand_frame(**L).matrix_rows())
    def test_point_roundtrip(self):
        f=c.hand_frame(**L);p=(.012,.045,.023);self.assertVector(f.to_local(f.to_world(p)),p)
    def test_other_hand_not_reflected_frame(self):
        ll={k:(-v[0],v[1],v[2]) for k,v in L.items()};f=c.hand_frame(**ll)
        c.validate_rigid(f.matrix_rows());self.assertFalse(f.x_points_toward_index)
    def test_rigid_covariance(self):
        f=c.hand_frame(**{k:c.apply_point(T,v) for k,v in L.items()})
        original=c.hand_frame(**L);p=(.01,.05,.03)
        self.assertVector(f.to_world(p),c.apply_point(T,original.to_world(p)))
    def test_reversed_tip_rejected(self):
        ll=dict(L,middle_tip=(0,-.1,0))
        with self.assertRaises(ValueError): c.hand_frame(**ll)
    def test_missing_palmar_side_rejected(self):
        with self.assertRaises(ValueError): c.hand_frame(**dict(L,palmar_point=(0,.04,0)))
    def test_zero_length_hand(self):
        with self.assertRaises(ValueError): c.hand_frame(**dict(L,middle_mcp=(0,0,0)))
    def test_degenerate_transverse(self):
        with self.assertRaises(ValueError): c.hand_frame(**dict(L,index_mcp=(0,.08,0),little_mcp=(0,.07,0)))
    def test_nonfinite_landmark(self):
        with self.assertRaises(ValueError): c.hand_frame(**dict(L,middle_mcp=(0,float('nan'),0)))
    def test_reflection_rejected(self):
        m=copy.deepcopy(I);m[0][0]=-1
        with self.assertRaises(ValueError): c.validate_rigid(m)
    def test_scale_rejected(self):
        m=copy.deepcopy(I);m[0][0]=2
        with self.assertRaises(ValueError): c.validate_rigid(m)
    def test_shear_rejected(self):
        m=copy.deepcopy(I);m[0][1]=.1
        with self.assertRaises(ValueError): c.validate_rigid(m)
    def test_inverse(self):
        p=(2,3,4);self.assertVector(c.apply_point(c.inverse_rigid(T),c.apply_point(T,p)),p)
    def test_relative_attachment(self):
        child=copy.deepcopy(I);child[2][3]=2
        local=c.relative_transform(T,child)
        got=c.multiply(T,local)
        for a,b in zip(got,child): self.assertVector(a,b)
    def test_cylinder_side_zero(self):
        self.assertAlmostEqual(c.cylinder_sample((.014,0,.05),(0,0,0),(0,0,.1),.014)['signed_distance_m'],0)
    def test_cylinder_inside(self):
        self.assertAlmostEqual(c.cylinder_sample((0,0,.05),(0,0,0),(0,0,.1),.014)['signed_distance_m'],-.014)
    def test_cylinder_radial_gap(self):
        self.assertAlmostEqual(c.cylinder_sample((.02,0,.05),(0,0,0),(0,0,.1),.014)['signed_distance_m'],.006)
    def test_cylinder_beyond_cap(self):
        s=c.cylinder_sample((0,0,.12),(0,0,0),(0,0,.1),.014)
        self.assertAlmostEqual(s['signed_distance_m'],.02);self.assertFalse(s['within_axial_span'])
    def test_cylinder_diagonal_corner_distance(self):
        s=c.cylinder_sample((.017,0,.104),(0,0,0),(0,0,.1),.014)
        self.assertAlmostEqual(s['signed_distance_m'],.005)
    def test_cylinder_rotated(self):
        args=[c.apply_point(T,v) for v in [(.02,0,.05),(0,0,0),(0,0,.1)]]
        self.assertAlmostEqual(c.cylinder_sample(*args,.014)['signed_distance_m'],.006)
    def test_bad_cylinder(self):
        for r in [-1,0,float('nan')]:
            with self.assertRaises(ValueError):c.cylinder_sample((0,0,0),(0,0,0),(0,0,1),r)
        with self.assertRaises(ValueError):c.cylinder_sample((0,0,0),(0,0,0),(0,0,0),1)
    def test_patch_pass_not_art(self):
        x=c.screen_patch([(.0142,0,.03),(.0141,0,.04),(.0143,0,.05)],(0,0,0),(0,0,.1),.014)
        self.assertEqual(x['status'],'PASS_SAMPLED_NUMERIC_SCREEN');self.assertFalse(x['visual_approval'])
    def test_thumb_penetration_rejected(self):
        x=c.screen_patch([(.0086,0,.03)],(0,0,0),(0,0,.1),.014)
        self.assertEqual(x['status'],'REVISE_NUMERIC_SCREEN');self.assertAlmostEqual(x['max_sampled_penetration_mm'],5.4)
    def test_gap_rejected(self):
        x=c.screen_patch([(.0187,0,.03)],(0,0,0),(0,0,.1),.014)
        self.assertEqual(x['status'],'REVISE_NUMERIC_SCREEN')
    def test_cap_touch_is_not_side_grip(self):
        x=c.screen_patch([(.014,0,0)],(0,0,0),(0,0,.1),.014)
        self.assertFalse(x['axial_region_valid']);self.assertEqual(x['status'],'REVISE_NUMERIC_SCREEN')
    def test_empty_patch(self):
        with self.assertRaises(ValueError):c.screen_patch([],(0,0,0),(0,0,.1),.014)
    def test_bad_tolerance(self):
        with self.assertRaises(ValueError):c.screen_patch([(.014,0,.05)],(0,0,0),(0,0,.1),.014,penetration_m=-1)
    def test_percentile(self): self.assertAlmostEqual(c.percentile([1,2,3,4],.5),2.5)

if __name__=='__main__': unittest.main(verbosity=2)
