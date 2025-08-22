import unittest
from ycleptic.yclept import Yclept
from ycleptic import resources
import os
from contextlib import redirect_stdout
import yaml

class TestYclept(unittest.TestCase):
    def test_userdict(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        with open('example1.yaml','r') as f:
            userdict=yaml.safe_load(f)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile,userdict=userdict)
        self.assertTrue('attribute_2' in Y["user"])
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'],'hello')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2_a_dict']['b'],765)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'],'we are done')
        # this is the default value:
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val2'],6)

    def test_update_user(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        with open('example1.yaml','r') as f:
            userdict=yaml.safe_load(f)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile,userdict=userdict)
        new_data = {
            'attribute_2': [
                {'attribute_2b': {'val1': 'new value', 'val2': 'updated value'}},
                {'attribute_2a': {'d2a_val1': 100, 'd2a_val2': 7, 'd2_a_dict': {'b': 800, 'c': 900}}},
                {'attribute_2b': {'val1': 'farewell', 'val2': 'the end'}}
            ]
        }
        Y.update_user(new_data)
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'], 'new value')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val1'], 100)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'], 'the end')

    def test_example1(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')
        self.assertTrue('attribute_2' in Y["user"])
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'],'hello')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2_a_dict']['b'],765)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'],'we are done')
        # this is the default value:
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val2'],6)
        
    def test_user_dump(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""

        with open('example1.yaml','w') as f:
            f.write(example1)

        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')        
        Y.dump_user('user-dump.yaml')
        self.assertTrue(os.path.exists('user-dump.yaml'))
        with open('user-dump.yaml','r') as f:
            user_dump=yaml.safe_load(f)
        tv=user_dump['attribute_3']['attribute_3_1']['attribute_3_1_1']['attribute_3_1_1_1']['d3111v1']
        self.assertEqual(tv,'ABC')

    def test_case_insensitive(self):
        example1="""
attribute_4: aBc123
attribute_5: A
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')
        self.assertTrue('attribute_4' in Y["user"])
        self.assertEqual(Y['user']['attribute_4'],'abc123')
        self.assertEqual(Y['user']['attribute_5'],'a')
        
    def test_dotfile1(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
      d2_a_dict:
        b: 765
        c: 789
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""
        dotfile_contents="""
attributes:
  - name: attribute_1
    type: dict
    text: This is a description of Attribute 1
    attributes:
      - name: attribute_1_1
        type: list
        text: This is a description of Attribute 1.1
        default:
          - 4
          - 5
          - 6
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        with open('rcfile.yaml','w') as f:
            f.write(dotfile_contents)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile,rcfile='rcfile.yaml')
        # Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')
        os.remove('rcfile.yaml')
        self.assertEqual(Y['user']['attribute_1']['attribute_1_1'],[4,5,6])

    def test_dotfile2(self):
        example1="""
attribute_2:
  - attribute_2b:
      val1: hello
      val2: let us begin
  - attribute_2a:
      d2a_val1: 99.999
  - attribute_2b:
      val1: goodbye
      val2: we are done
attribute_1:
  attribute_1_2: valA
"""
        dotfile_contents="""
attributes:
  - name: attribute_2
    type: list
    text: Attribute 2 is interpretable as an ordered list of attributes
    attributes:
      - name: attribute_2a
        type: dict
        text: Attribute 2a is one possible attribute in a user's list
        attributes:
          - name: d2a_val1
            type: float
            text: A floating point value for Value 1 of Attribute 2a
            default: 2.0
          - name: d2a_val2
            type: int
            text: An int for Value 2 of Attribute 2a
            default: 7
          - name: d2_a_dict
            type: dict
            text: this is a dict
            default:
              a: 1234
              b: 5678
              c: 9877
"""
        with open('example1.yaml','w') as f:
            f.write(example1)
        with open('rcfile.yaml','w') as f:
            f.write(dotfile_contents)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        ufile=os.path.join('example1.yaml')
        Y=Yclept(bfile,userfile=ufile,rcfile='rcfile.yaml')
        # Y=Yclept(bfile,userfile=ufile)
        os.remove('example1.yaml')
        os.remove('rcfile.yaml')
        hits=[]
        for member in Y['user']['attribute_2']:
            dname=list(member.keys())[0]
            if dname=='attribute_2a':
                hits.append(Y['user']['attribute_2'].index(member))
        for hit in hits:
            self.assertEqual(Y['user']['attribute_2'][hit]['attribute_2a']['d2_a_dict'],{'a':1234,'b':5678,'c':9877})

    def test_console_help(self):
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile)
        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help([]);
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,'    attribute_1 ->\n    attribute_2 ->\n    attribute_3 ->\n    attribute_4\n    attribute_5\n')

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['attribute_1']);
        ref_str="""
attribute_1:
    This is a description of Attribute 1

base|attribute_1
    attribute_1_1
    attribute_1_2
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['attribute_1','attribute_1_1']);
        ref_str="""
attribute_1_1:
    This is a description of Attribute 1.1
    default: [1, 2, 3]

All subattributes at the same level as 'attribute_1_1':

base|attribute_1
    attribute_1_1
    attribute_1_2
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['attribute_2']);
        ref_str="""
attribute_2:
    Attribute 2 is interpretable as an ordered list of attributes

base|attribute_2
    attribute_2a ->
    attribute_2b ->
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['attribute_2','attribute_2a']);
        ref_str="""
attribute_2a:
    Attribute 2a is one possible attribute in a user's list

base|attribute_2->attribute_2a
    d2a_val1
    d2a_val2
    d2_a_dict
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

    def test_makedoc(self):
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile)
        Y.make_doctree('ydoc')
        self.assertTrue(os.path.exists('ydoc.rst'))
        ref_str=""".. _ydoc:

``ydoc``
========

Top-level attributes

Single-valued parameters:

  * ``attribute_4``: This is a description of Attribute 4

  * ``attribute_5``: This is a description of Attribute 5



Subattributes:

.. toctree::
   :maxdepth: 1

   ydoc/attribute_1
   ydoc/attribute_2
   ydoc/attribute_3


----
"""
        with open('ydoc.rst','r') as f:
            test_str=f.read()
            # remove everything after '----' since it will have a date stamp
            test_str=test_str.split('----')[0]+'----\n'
        self.assertEqual(test_str,ref_str)

        self.assertTrue(os.path.isdir('ydoc'))
        self.assertTrue(os.path.exists(os.path.join('ydoc','attribute_1.rst')))
        self.assertTrue(os.path.isdir(os.path.join('ydoc','attribute_1')))
        self.assertTrue(os.path.exists(os.path.join('ydoc','attribute_1','attribute_1_1.rst')))
