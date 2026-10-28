import importlib.util,pathlib,unittest,copy
p=pathlib.Path(__file__).resolve().parents[1]/'tools/check_planar_boxes.py';s=importlib.util.spec_from_file_location('checker',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
EX={'dimension':2,'n':3,'edges':[[1,2],[1,3],[2,3]],'lengths':['6','5','5'],'pinned':[1,2],'unknowns':['x3','y3'],'boxes':[[['29/10','31/10'],['39/10','41/10']],[['29/10','31/10'],['-41/10','-39/10']]],'claimed_real_count':2}
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
if __name__=='__main__':unittest.main()
