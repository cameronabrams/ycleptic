import shutil
import unittest
from contextlib import redirect_stdout
import os
import yaml

from ycleptic.yclept import Yclept
from ycleptic import resources
from ycleptic import YclepticError
from ycleptic.cli import config_help
from ycleptic.dictthings import special_update
from ycleptic.stringthings import oxford, generate_footer, dict_to_rst_yaml_block

BFILE = os.path.join(os.path.dirname(resources.__file__), 'example_base.yaml')

EXAMPLE1_YAML = """
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


class TestYclept(unittest.TestCase):
    def tearDown(self):
        for fname in [
            'example1.yaml',
            'user-dump.yaml',
            'console-out.txt',
            'rcfile.yaml',
            'req_base.yaml',
            'type_base.yaml',
        ]:
            if os.path.exists(fname):
                os.remove(fname)
        if os.path.exists('ydoc.rst'):
            os.remove('ydoc.rst')
        if os.path.isdir('ydoc'):
            shutil.rmtree('ydoc')

    # ------------------------------------------------------------------
    # Existing tests (preserved)
    # ------------------------------------------------------------------

    def test_userdict(self):
        with open('example1.yaml', 'w') as f:
            f.write(EXAMPLE1_YAML)
        with open('example1.yaml', 'r') as f:
            userdict = yaml.safe_load(f)
        Y = Yclept(BFILE, userdict=userdict)
        self.assertTrue('attribute_2' in Y['user'])
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'], 'hello')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2_a_dict']['b'], 765)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'], 'we are done')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val2'], 6)

    def test_update_user(self):
        with open('example1.yaml', 'w') as f:
            f.write(EXAMPLE1_YAML)
        with open('example1.yaml', 'r') as f:
            userdict = yaml.safe_load(f)
        Y = Yclept(BFILE, userdict=userdict)
        new_data = {
            'attribute_2': [
                {'attribute_2b': {'val1': 'new value', 'val2': 'updated value'}},
                {
                    'attribute_2a': {
                        'd2a_val1': 100,
                        'd2a_val2': 7,
                        'd2_a_dict': {'b': 800, 'c': 900},
                    }
                },
                {'attribute_2b': {'val1': 'farewell', 'val2': 'the end'}},
            ]
        }
        Y.update_user(new_data)
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'], 'new value')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val1'], 100)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'], 'the end')

    def test_example1(self):
        with open('example1.yaml', 'w') as f:
            f.write(EXAMPLE1_YAML)
        Y = Yclept(BFILE, userfile='example1.yaml')
        self.assertTrue('attribute_2' in Y['user'])
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2b']['val1'], 'hello')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2_a_dict']['b'], 765)
        self.assertEqual(Y['user']['attribute_2'][2]['attribute_2b']['val2'], 'we are done')
        self.assertEqual(Y['user']['attribute_2'][1]['attribute_2a']['d2a_val2'], 6)

    def test_user_dump(self):
        with open('example1.yaml', 'w') as f:
            f.write(EXAMPLE1_YAML)
        Y = Yclept(BFILE, userfile='example1.yaml')
        Y.dump_user('user-dump.yaml')
        self.assertTrue(os.path.exists('user-dump.yaml'))
        with open('user-dump.yaml', 'r') as f:
            user_dump = yaml.safe_load(f)
        tv = user_dump['attribute_3']['attribute_3_1']['attribute_3_1_1']['attribute_3_1_1_1'][
            'd3111v1'
        ]
        self.assertEqual(tv, 'ABC')

    def test_case_insensitive(self):
        example1 = 'attribute_4: aBc123\nattribute_5: A\n'
        with open('example1.yaml', 'w') as f:
            f.write(example1)
        Y = Yclept(BFILE, userfile='example1.yaml')
        self.assertTrue('attribute_4' in Y['user'])
        self.assertEqual(Y['user']['attribute_4'], 'abc123')
        self.assertEqual(Y['user']['attribute_5'], 'a')

    def test_dotfile1(self):
        dotfile_contents = """
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
        with open('example1.yaml', 'w') as f:
            f.write(EXAMPLE1_YAML)
        with open('rcfile.yaml', 'w') as f:
            f.write(dotfile_contents)
        Y = Yclept(BFILE, userfile='example1.yaml', rcfile='rcfile.yaml')
        self.assertEqual(Y['user']['attribute_1']['attribute_1_1'], [4, 5, 6])

    def test_dotfile2(self):
        example1 = """
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
        dotfile_contents = """
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
        with open('example1.yaml', 'w') as f:
            f.write(example1)
        with open('rcfile.yaml', 'w') as f:
            f.write(dotfile_contents)
        Y = Yclept(BFILE, userfile='example1.yaml', rcfile='rcfile.yaml')
        hits = []
        for member in Y['user']['attribute_2']:
            dname = list(member.keys())[0]
            if dname == 'attribute_2a':
                hits.append(Y['user']['attribute_2'].index(member))
        for hit in hits:
            self.assertEqual(
                Y['user']['attribute_2'][hit]['attribute_2a']['d2_a_dict'],
                {'a': 1234, 'b': 5678, 'c': 9877},
            )

    def test_console_help(self):
        Y = Yclept(BFILE)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help([])
        with open('console-out.txt', 'r') as f:
            test_str = f.read()
        self.assertEqual(
            test_str,
            '    attribute_1 ->\n    attribute_2 ->\n    attribute_3 ->\n    attribute_4\n    attribute_5\n',
        )

        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help(['attribute_1'])
        ref_str = """
attribute_1:
    This is a description of Attribute 1

base|attribute_1
    attribute_1_1
    attribute_1_2
"""
        with open('console-out.txt', 'r') as f:
            self.assertEqual(f.read(), ref_str)

        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help(['attribute_1', 'attribute_1_1'])
        ref_str = """
attribute_1_1:
    This is a description of Attribute 1.1
    default: [1, 2, 3]

All subattributes at the same level as 'attribute_1_1':

base|attribute_1
    attribute_1_1
    attribute_1_2
"""
        with open('console-out.txt', 'r') as f:
            self.assertEqual(f.read(), ref_str)

        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help(['attribute_2'])
        ref_str = """
attribute_2:
    Attribute 2 is interpretable as an ordered list of attributes

base|attribute_2
    attribute_2a ->
    attribute_2b ->
"""
        with open('console-out.txt', 'r') as f:
            self.assertEqual(f.read(), ref_str)

        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help(['attribute_2', 'attribute_2a'])
        ref_str = """
attribute_2a:
    Attribute 2a is one possible attribute in a user's list

base|attribute_2->attribute_2a
    d2a_val1
    d2a_val2
    d2_a_dict
"""
        with open('console-out.txt', 'r') as f:
            self.assertEqual(f.read(), ref_str)

    def test_makedoc(self):
        Y = Yclept(BFILE)
        Y.make_doctree('ydoc')
        self.assertTrue(os.path.exists('ydoc.rst'))
        ref_str = """.. _ydoc:

``ydoc``
========

Top-level attributes

Single-valued attributes:

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
        with open('ydoc.rst', 'r') as f:
            test_str = f.read()
            test_str = test_str.split('----')[0] + '----\n'
        self.assertEqual(test_str, ref_str)
        self.assertTrue(os.path.isdir('ydoc'))
        self.assertTrue(os.path.exists(os.path.join('ydoc', 'attribute_1.rst')))
        self.assertTrue(os.path.isdir(os.path.join('ydoc', 'attribute_1')))
        self.assertTrue(os.path.exists(os.path.join('ydoc', 'attribute_1', 'attribute_1_1.rst')))

    # ------------------------------------------------------------------
    # Validation / error-path tests
    # ------------------------------------------------------------------

    def test_invalid_attribute_name(self):
        """A key not in the base config raises YclepticError."""
        with open('example1.yaml', 'w') as f:
            f.write('bad_attribute: hello\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_choices_valid(self):
        """attribute_5 accepts a value in its choices list (case-insensitive)."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_5: B\n')
        Y = Yclept(BFILE, userfile='example1.yaml')
        self.assertEqual(Y['user']['attribute_5'], 'b')

    def test_choices_case_sensitive_invalid(self):
        """A value outside a case-sensitive attribute's choices is rejected."""
        # attribute_1_2 has choices [valA, valB] and is case-sensitive by default,
        # so 'ValA' (wrong case) must be rejected.
        with open('example1.yaml', 'w') as f:
            f.write('attribute_1:\n  attribute_1_2: ValA\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_choices_invalid(self):
        """attribute_5 rejects a value not in its choices list."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_5: x\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_required_attribute_missing(self):
        """A required attribute with no default and no user value raises YclepticError."""
        base_config = """
attributes:
  - name: myattr
    type: str
    text: A required string
    required: True
"""
        with open('req_base.yaml', 'w') as f:
            f.write(base_config)
        with self.assertRaises(YclepticError):
            Yclept('req_base.yaml', userdict={})

    def test_wrong_type_for_dict_attribute(self):
        """Providing a scalar where a dict is expected raises YclepticError."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_1: not_a_dict\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_config_help_exit_at_end(self):
        """The config-help CLI honors --exit-at-end, exiting when traversal ends."""
        from argparse import Namespace

        args = Namespace(config=BFILE, arglist=[], exit_at_end=True, i=False)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                with self.assertRaises(SystemExit):
                    config_help(args)

    # ------------------------------------------------------------------
    # Scalar type validation
    # ------------------------------------------------------------------

    def test_int_attribute_rejects_string(self):
        """A string value for an int attribute raises YclepticError."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_2:\n  - attribute_2a:\n      d2a_val2: not_an_int\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_int_attribute_rejects_bool(self):
        """A boolean is not accepted where an int is declared."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_2:\n  - attribute_2a:\n      d2a_val2: true\n')
        with self.assertRaises(YclepticError):
            Yclept(BFILE, userfile='example1.yaml')

    def test_float_attribute_accepts_int(self):
        """An int is accepted where a float is declared (widening), and preserved."""
        with open('example1.yaml', 'w') as f:
            f.write('attribute_2:\n  - attribute_2a:\n      d2a_val1: 100\n')
        Y = Yclept(BFILE, userfile='example1.yaml')
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2a']['d2a_val1'], 100)

    def test_bool_attribute_validation(self):
        """A bool attribute accepts booleans and rejects other types."""
        with open('type_base.yaml', 'w') as f:
            f.write(
                'attributes:\n  - name: flag\n    type: bool\n    text: a boolean\n    default: false\n'
            )
        Y = Yclept('type_base.yaml', userdict={'flag': True})
        self.assertIs(Y['user']['flag'], True)
        with self.assertRaises(YclepticError):
            Yclept('type_base.yaml', userdict={'flag': 'yes'})

    def test_tuple_attribute_coerced_and_validated(self):
        """A tuple attribute accepts a YAML sequence (stored as a tuple) and rejects a scalar."""
        with open('type_base.yaml', 'w') as f:
            f.write(
                'attributes:\n  - name: coords\n    type: tuple\n    text: a tuple\n    default: []\n'
            )
        Y = Yclept('type_base.yaml', userdict={'coords': [1, 2, 3]})
        self.assertEqual(Y['user']['coords'], (1, 2, 3))
        self.assertIsInstance(Y['user']['coords'], tuple)
        with self.assertRaises(YclepticError):
            Yclept('type_base.yaml', userdict={'coords': 5})

    # ------------------------------------------------------------------
    # make_default_specs
    # ------------------------------------------------------------------

    def test_make_default_specs(self):
        """make_default_specs returns defaults for a top-level dict attribute."""
        Y = Yclept(BFILE)
        result = Y.make_default_specs('attribute_1')
        self.assertIn('attribute_1_1', result)
        self.assertEqual(result['attribute_1_1'], [1, 2, 3])
        self.assertIn('attribute_1_2', result)
        self.assertIsNone(result['attribute_1_2'])

    def test_make_default_specs_nested(self):
        """make_default_specs can drill into a nested attribute."""
        Y = Yclept(BFILE)
        result = Y.make_default_specs('attribute_1', 'attribute_1_1')
        self.assertIn('attribute_1_1', result)
        self.assertEqual(result['attribute_1_1'], [1, 2, 3])

    def test_make_default_specs_invalid(self):
        """make_default_specs raises YclepticError for an unrecognized attribute."""
        Y = Yclept(BFILE)
        with self.assertRaises(YclepticError):
            Y.make_default_specs('not_a_real_attribute')

    # ------------------------------------------------------------------
    # Utility function tests
    # ------------------------------------------------------------------

    def test_special_update_list_merge(self):
        """special_update appends list values without duplicating existing entries."""
        d1 = {'a': [1, 2]}
        d2 = {'a': [2, 3]}
        result = special_update(d1, d2)
        self.assertEqual(result['a'], [1, 2, 3])

    def test_special_update_dict_merge(self):
        """special_update merges nested dicts."""
        d1 = {'b': {'x': 1}}
        d2 = {'b': {'y': 2}}
        result = special_update(d1, d2)
        self.assertEqual(result['b'], {'x': 1, 'y': 2})

    def test_special_update_scalar_overwrite(self):
        """special_update overwrites scalar values."""
        d1 = {'c': 'old', 'd': 1}
        d2 = {'c': 'new', 'e': 'extra'}
        result = special_update(d1, d2)
        self.assertEqual(result['c'], 'new')
        self.assertEqual(result['d'], 1)
        self.assertEqual(result['e'], 'extra')

    def test_special_update_merges_into_empty_existing(self):
        """An existing empty (falsy) container is merged into, not treated as absent."""
        d1 = {'items': [], 'opts': {}}
        d2 = {'items': [1, 2], 'opts': {'x': 1}}
        result = special_update(d1, d2)
        # the original empty containers are populated in place
        self.assertEqual(result['items'], [1, 2])
        self.assertEqual(result['opts'], {'x': 1})
        self.assertIs(result['items'], d1['items'])
        self.assertIs(result['opts'], d1['opts'])

    def test_oxford_empty(self):
        self.assertEqual(oxford([]), '')

    def test_oxford_one(self):
        self.assertEqual(oxford(['a']), 'a')

    def test_oxford_two(self):
        self.assertEqual(oxford(['a', 'b']), 'a or b')

    def test_oxford_three_plus(self):
        self.assertEqual(oxford(['a', 'b', 'c']), 'a, b, or c')
        self.assertEqual(oxford(['a', 'b', 'c', 'd']), 'a, b, c, or d')

    def test_oxford_conjunction(self):
        self.assertEqual(oxford(['a', 'b'], conjunction='and'), 'a and b')
        self.assertEqual(oxford(['a', 'b', 'c'], conjunction='and'), 'a, b, and c')

    def test_generate_footer_all_styles(self):
        """All documented footer styles produce non-empty strings containing the app name."""
        for style in ['paragraph', 'comment', 'rubric', 'note', 'raw-html']:
            result = generate_footer(app_name='testapp', version='9.9', style=style)
            self.assertIsInstance(result, str)
            self.assertIn('testapp', result)
            self.assertIn('9.9', result)

    def test_generate_footer_invalid_style(self):
        with self.assertRaises(ValueError):
            generate_footer(style='invalid')

    def test_dict_to_rst_yaml_block(self):
        data = {'key': 'value', 'num': 42}
        result = dict_to_rst_yaml_block(data)
        self.assertTrue(result.startswith('.. code-block:: yaml'))
        self.assertIn('key', result)
        self.assertIn('value', result)
        self.assertIn('42', result)

    def test_dict_to_rst_yaml_block_multiline(self):
        """Multiline string values are rendered with block scalar style."""
        data = {'msg': 'line one\nline two'}
        result = dict_to_rst_yaml_block(data)
        self.assertIn('.. code-block:: yaml', result)
        self.assertIn('msg', result)

    # ------------------------------------------------------------------
    # Backward-compatibility shim for the old ycleptic.src layout
    # ------------------------------------------------------------------

    def test_deprecated_src_shim(self):
        """The old ``ycleptic.src.*`` paths still resolve, but emit a DeprecationWarning."""
        import importlib
        import sys
        import warnings

        import ycleptic.yclept

        # Force a fresh import of the shim so the warning fires deterministically.
        for mod in [
            m for m in list(sys.modules) if m == 'ycleptic.src' or m.startswith('ycleptic.src.')
        ]:
            del sys.modules[mod]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            shim = importlib.import_module('ycleptic.src.yclept')
        self.assertIs(shim.Yclept, ycleptic.yclept.Yclept)
        self.assertTrue(any(issubclass(c.category, DeprecationWarning) for c in caught))
