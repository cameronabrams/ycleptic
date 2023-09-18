import unittest
from ycleptic.yclept import Yclept
from ycleptic import resources
import os

class TestYclept(unittest.TestCase):
    def test_example1(self):
        example1="""
directive_2:
  - directive_2b:
      val1: hello
      val2: let us begin
  - directive_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - directive_2b:
      val1: goodbye
      val2: we are done
directive_1:
  directive_1_2: valA
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')
        self.assertTrue('directive_2' in Y["user"])
        print(Y["user"]["directive_2"][0])
        self.assertEqual(Y['user']['directive_2'][0]['directive_2b']['val1'],'hello')
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2_a_dict']['b'],765)
        self.assertEqual(Y['user']['directive_2'][2]['directive_2b']['val2'],'we are done')
        # this is the default value:
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2a_val2'],6)