import unittest
from ycleptic.yclept import Yclept
from ycleptic import resources
import os
from contextlib import redirect_stdout
import yaml

class TestYclept(unittest.TestCase):
    def test_userdict(self):
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
        with open('example1.yaml','r') as f:
            userdict=yaml.safe_load(f)
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile,userdict=userdict)
        self.assertTrue('directive_2' in Y["user"])
        self.assertEqual(Y['user']['directive_2'][0]['directive_2b']['val1'],'hello')
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2_a_dict']['b'],765)
        self.assertEqual(Y['user']['directive_2'][2]['directive_2b']['val2'],'we are done')
        # this is the default value:
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2a_val2'],6)

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
        self.assertEqual(Y['user']['directive_2'][0]['directive_2b']['val1'],'hello')
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2_a_dict']['b'],765)
        self.assertEqual(Y['user']['directive_2'][2]['directive_2b']['val2'],'we are done')
        # this is the default value:
        self.assertEqual(Y['user']['directive_2'][1]['directive_2a']['d2a_val2'],6)
        
    def test_user_dump(self):
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
        Y.dump_user('user-dump.yaml')
        self.assertTrue(os.path.exists('user-dump.yaml'))
        with open('user-dump.yaml','r') as f:
            user_dump=yaml.safe_load(f)
        tv=user_dump['directive_3']['directive_3_1']['directive_3_1_1']['directive_3_1_1_1']['d3111v1']
        self.assertEqual(tv,'ABC')

    def test_dotfile1(self):
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
        dotfile_contents="""
directives:
  - name: directive_1
    type: dict
    text: This is a description of Directive 1
    directives:
      - name: directive_1_1
        type: list
        text: This is a description of Directive 1.1
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
        self.assertEqual(Y['user']['directive_1']['directive_1_1'],[4,5,6])

    def test_dotfile2(self):
        example1="""
directive_2:
  - directive_2b:
      val1: hello
      val2: let us begin
  - directive_2a:
      d2a_val1: 99.999
  - directive_2b:
      val1: goodbye
      val2: we are done
directive_1:
  directive_1_2: valA
"""
        dotfile_contents="""
directives:
  - name: directive_2
    type: list
    text: Directive 2 is interpretable as an ordered list of directives
    directives:
      - name: directive_2a
        type: dict
        text: Directive 2a is one possible directive in a user's list
        directives:
          - name: d2a_val1
            type: float
            text: A floating point value for Value 1 of Directive 2a
            default: 2.0
          - name: d2a_val2
            type: int
            text: An int for Value 2 of Directive 2a
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
        for member in Y['user']['directive_2']:
            dname=list(member.keys())[0]
            if dname=='directive_2a':
                hits.append(Y['user']['directive_2'].index(member))
        for hit in hits:
            self.assertEqual(Y['user']['directive_2'][hit]['directive_2a']['d2_a_dict'],{'a':1234,'b':5678,'c':9877})

    def test_console_help(self):
        bdir=os.path.dirname(resources.__file__)
        bfile=os.path.join(bdir,'example_base.yaml')
        Y=Yclept(bfile)
        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help([]);
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,'    directive_1 ->\n    directive_2 ->\n    directive_3 ->\n')

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['directive_1']);
        ref_str="""
directive_1:
    This is a description of Directive 1

base|directive_1
    directive_1_1
    directive_1_2
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['directive_1','directive_1_1']);
        ref_str="""
directive_1_1:
    This is a description of Directive 1.1
    default: [1, 2, 3]

All subdirectives at the same level as 'directive_1_1':

base|directive_1
    directive_1_1
    directive_1_2
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['directive_2']);
        ref_str="""
directive_2:
    Directive 2 is interpretable as an ordered list of directives

base|directive_2
    directive_2a ->
    directive_2b ->
"""
        with open('console-out.txt','r') as f:
          test_str=f.read()
          self.assertEqual(test_str,ref_str)

        with open('console-out.txt','w') as f:
          with redirect_stdout(f):
              Y.console_help(['directive_2','directive_2a']);
        ref_str="""
directive_2a:
    Directive 2a is one possible directive in a user's list

base|directive_2->directive_2a
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

Top-level directives

Subdirectives:

.. toctree::
   :maxdepth: 1

   ydoc/directive_1
   ydoc/directive_2
   ydoc/directive_3


"""
        with open('ydoc.rst','r') as f:
            test_str=f.read()
        self.assertEqual(test_str,ref_str)

        self.assertTrue(os.path.isdir('ydoc'))
        self.assertTrue(os.path.exists(os.path.join('ydoc','directive_1.rst')))
        self.assertTrue(os.path.isdir(os.path.join('ydoc','directive_1')))
        self.assertTrue(os.path.exists(os.path.join('ydoc','directive_1','directive_1_1.rst')))
