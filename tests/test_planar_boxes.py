import importlib.util,io,json,pathlib,unittest,copy
from fractions import Fraction as Q
p=pathlib.Path(__file__).resolve().parents[1]/'tools/check_planar_boxes.py';s=importlib.util.spec_from_file_location('checker',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
EX={'dimension':2,'n':3,'edges':[[1,2],[1,3],[2,3]],'lengths':['6','5','5'],'pinned':[1,2],'unknowns':['x3','y3'],'boxes':[[['29/10','31/10'],['39/10','41/10']],[['29/10','31/10'],['-41/10','-39/10']]],'claimed_real_count':2}
TRI_NUMERIC='''{"dimension":2,"n":3,"edges":[[1,2],[1,3],[2,3]],"lengths":["6","5","5"],"pinned":[1,2],"unknowns":["x3","y3"],"boxes":[[[2.9,3.1],[3.9,4.1]],[[2.9,3.1],[-4.1,-3.9]]],"claimed_real_count":2}'''
class Controls(unittest.TestCase):
 def test_triangle(self):self.assertEqual(m.check(EX)['certified_non_degenerate_boxes'],2)
 def test_wrong_length(self):
  d=copy.deepcopy(EX);d['lengths'][1]='7'
  with self.assertRaises(ValueError):m.check(d)
 def test_overlap(self):
  d=copy.deepcopy(EX);d['boxes'][1]=copy.deepcopy(d['boxes'][0])
  with self.assertRaises(ValueError):m.check(d)
 def test_bad_count(self):
  d=dict(EX,claimed_real_count=3)
  with self.assertRaises(ValueError):m.check(d)
 def test_degenerate_box(self):
  d=copy.deepcopy(EX);d['boxes'][0][1]=['0','0']
  with self.assertRaises(ValueError):m.check(d)
 def test_wrong_unknown_order(self):
  with self.assertRaises(ValueError):m.check(dict(EX,unknowns=['y3','x3']))
 def test_json_number_endpoints_are_exact(self):
  d=m.load_certificate(io.StringIO(TRI_NUMERIC))
  self.assertEqual(d['boxes'][0][0],[Q(29,10),Q(31,10)])
  self.assertEqual(d['boxes'][0][1],[Q(39,10),Q(41,10)])
  self.assertEqual(m.check(d)['certified_non_degenerate_boxes'],2)
 def test_float_json_numbers_rejected_without_exact_loader(self):
  with self.assertRaises(ValueError):m.check(json.loads(TRI_NUMERIC))
if __name__=='__main__':unittest.main()
