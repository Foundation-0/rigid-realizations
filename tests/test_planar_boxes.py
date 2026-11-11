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
 def test_non_finite_json_constants_rejected_on_load(self):
  for c in ('NaN','Infinity','-Infinity'):
   for field,text in (('length',TRI_NUMERIC.replace('"lengths":["6","5","5"]','"lengths":[6,'+c+',5]')),('box endpoint',TRI_NUMERIC.replace('[2.9,3.1]','['+c+',3.1]',1))):
    with self.subTest(constant=c,field=field):
     self.assertNotEqual(text,TRI_NUMERIC)
     with self.assertRaisesRegex(ValueError,'non-finite JSON number'):m.load_certificate(io.StringIO(text))
 def test_non_finite_values_rejected_by_check(self):
  for v in (float('nan'),float('inf'),float('-inf'),'NaN','Infinity','-Infinity'):
   with self.subTest(value=v):
    d=copy.deepcopy(EX);d['lengths'][1]=v
    with self.assertRaises(ValueError):m.check(d)
    d=copy.deepcopy(EX);d['boxes'][0][0][1]=v
    with self.assertRaises(ValueError):m.check(d)
 def test_zero_length_edge_rejected(self):
  d=copy.deepcopy(EX);d['lengths'][2]='0'
  with self.assertRaisesRegex(ValueError,'bad edge/length shape'):m.check(d)
 def test_bad_edges_rejected(self):
  for edges in ([[1,2],[1,3],[2,4]],[[1,2],[1,3],[0,3]],[[1,2],[1,3],[3,3]],[[1,2],[1,3],[2,3,1]],[[1,2],[1,3],[2]],[[1,2],[1,3],[1,3]],[[1,2],[1,3],[2,'3']],[[1,2],[1,3],[2,3.0]],[[1,2],[1,3],[True,3]],[[1,2],[1,3],23]):
   with self.subTest(edges=edges):
    with self.assertRaisesRegex(ValueError,'invalid edges'):m.check(dict(EX,edges=edges))
 def test_wrong_edge_count_rejected(self):
  for k in (2,4):
   edges=[[1,2],[1,3],[2,3],[1,2]][:k];lengths=['6','5','5','6'][:k]
   with self.subTest(count=k):
    with self.assertRaisesRegex(ValueError,'bad edge/length shape'):m.check(dict(EX,edges=edges,lengths=lengths))
if __name__=='__main__':unittest.main()
