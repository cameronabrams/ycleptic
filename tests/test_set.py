import shutil
import unittest
from contextlib import redirect_stdout, redirect_stderr
import os
import yaml

from ycleptic.yclept import Yclept
from ycleptic import resources
from ycleptic import YclepticError, YclepticSpecWarning
from ycleptic.speccheck import check_base_spec
from ycleptic.cli import config_help, check_spec
from ycleptic.dictthings import special_update
from ycleptic.stringthings import oxford, generate_footer, dict_to_rst_yaml_block

BFILE = os.path.join(os.path.dirname(resources.__file__), 'example_base.yaml')

# A base spec exercising every silent-typo trap the spec checker looks for.
BAD_SPEC_YAML = """
attributes:
  - name: a_opts
    type: str
    text: uses options instead of choices
    options: [red, green]
    default: red
  - name: a_string
    type: string
    text: uses type string instead of str
    choices: [red, green]
    default: red
  - name: an_int
    type: int
    text: choices on a non-str attribute
    choices: [1, 2, 3]
    default: 1
  - name: nested
    type: dict
    text: a nested block
    attributes:
      - name: deep
        type: str
        text: a misspelled key one level down
        chioces: [red, green]
        docs:
          titel: a misspelled docs key
  - name: untyped
    text: no type declared at all
"""

# The one trap above that stops a load outright, so tests can drop it.
UNTYPED_ATTRIBUTE = """  - name: untyped
    text: no type declared at all
"""

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
    A list you supply is added after this default.

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

    def test_console_help_eof_quits_cleanly(self):
        """EOF on stdin ends an interactive help session as if the user typed '!'."""
        from unittest.mock import patch

        Y = Yclept(BFILE)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                with patch('builtins.input', side_effect=EOFError):
                    Y.console_help([], interactive_prompt='help: ')
        with open('console-out.txt', 'r') as f:
            self.assertIn('! quit', f.read())

    def test_console_help_eof_after_bad_choice_quits_cleanly(self):
        """EOF also ends the session from the re-prompt after an unrecognized choice."""
        from unittest.mock import patch

        Y = Yclept(BFILE)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                with patch('builtins.input', side_effect=['bogus', EOFError]):
                    Y.console_help([], interactive_prompt='help: ')
        with open('console-out.txt', 'r') as f:
            self.assertIn('bogus not recognized.', f.read())

    def test_console_help_keyboard_interrupt_quits_cleanly(self):
        """Ctrl-C at the prompt ends the session cleanly rather than raising."""
        from unittest.mock import patch

        Y = Yclept(BFILE)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                with patch('builtins.input', side_effect=KeyboardInterrupt):
                    Y.console_help([], interactive_prompt='help: ')
        with open('console-out.txt', 'r') as f:
            self.assertIn('! quit', f.read())

    # ------------------------------------------------------------------
    # Base-spec validation
    # ------------------------------------------------------------------

    def test_shipped_example_base_spec_is_clean(self):
        """The shipped example must not trip its own spec checker."""
        with open(BFILE, 'r') as f:
            base = yaml.safe_load(f)
        self.assertEqual(check_base_spec(base), [])

    def test_spec_check_flags_options_instead_of_choices(self):
        """'options' is read by nothing, so a schema using it is unvalidated."""
        base = yaml.safe_load(BAD_SPEC_YAML)
        problems = check_base_spec(base)
        opt = [p for p in problems if "unrecognized key 'options'" in p]
        self.assertEqual(len(opt), 1)
        self.assertIn("attribute 'a_opts'", opt[0])
        self.assertIn("did you mean 'choices'?", opt[0])

    def test_spec_check_flags_string_instead_of_str(self):
        """'string' matches no branch, so the attribute gets no string handling."""
        base = yaml.safe_load(BAD_SPEC_YAML)
        problems = check_base_spec(base)
        typ = [p for p in problems if "unrecognized type 'string'" in p]
        self.assertEqual(len(typ), 1)
        self.assertIn("attribute 'a_string'", typ[0])
        self.assertIn("did you mean 'str'?", typ[0])

    def test_spec_check_flags_choices_on_non_str(self):
        """'choices' is enforced only on str attributes; elsewhere it is inert."""
        base = yaml.safe_load(BAD_SPEC_YAML)
        problems = check_base_spec(base)
        ch = [p for p in problems if "'choices' is only enforced" in p]
        self.assertEqual(len(ch), 1)
        self.assertIn("attribute 'an_int'", ch[0])

    def test_spec_check_reports_nested_path_and_docs_keys(self):
        """Problems name the full attribute path, including inside a docs block."""
        base = yaml.safe_load(BAD_SPEC_YAML)
        problems = check_base_spec(base)
        self.assertTrue(
            any("attribute 'nested->deep': unrecognized key 'chioces'" in p for p in problems)
        )
        self.assertTrue(any("'titel' in its 'docs' block" in p for p in problems))

    def test_spec_check_flags_missing_type(self):
        base = yaml.safe_load(BAD_SPEC_YAML)
        problems = check_base_spec(base)
        self.assertTrue(any("attribute 'untyped': no 'type' declared" in p for p in problems))

    def test_bad_spec_warns_by_default(self):
        """A questionable spec still loads, but says so."""
        specfile = 'spec-check-base.yaml'
        with open(specfile, 'w') as f:
            f.write(BAD_SPEC_YAML.replace(UNTYPED_ATTRIBUTE, ''))
        with self.assertWarns(YclepticSpecWarning) as cm:
            Y = Yclept(specfile, userdict={'a_opts': 'red'})
        self.assertIn('does not act on', str(cm.warning))
        self.assertEqual(Y['user']['a_opts'], 'red')

    def test_attribute_with_no_type_reports_cleanly(self):
        """A spec attribute with no declared type is an error, not a KeyError."""
        specfile = 'spec-check-base.yaml'
        with open(specfile, 'w') as f:
            f.write(BAD_SPEC_YAML)
        with self.assertWarns(YclepticSpecWarning):
            with self.assertRaises(YclepticError) as cm:
                Yclept(specfile, userdict={})
        self.assertIn('declares no type', str(cm.exception))

    def test_bad_spec_raises_under_strict_spec(self):
        specfile = 'spec-check-base.yaml'
        with open(specfile, 'w') as f:
            f.write(BAD_SPEC_YAML)
        with self.assertRaises(YclepticError) as cm:
            Yclept(specfile, userdict={}, strict_spec=True)
        self.assertIn("unrecognized key 'options'", str(cm.exception))

    def test_good_spec_neither_warns_nor_raises(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter('error', YclepticSpecWarning)
            Yclept(BFILE, strict_spec=True)

    def test_check_spec_cli_reports_and_exits_nonzero(self):
        """The check-spec subcommand gates CI on a clean base spec."""
        from argparse import Namespace

        specfile = 'spec-check-base.yaml'
        with open(specfile, 'w') as f:
            f.write(BAD_SPEC_YAML)
        with open('console-out.txt', 'w') as f:
            with redirect_stderr(f):
                with self.assertRaises(SystemExit) as cm:
                    check_spec(Namespace(config=specfile))
        self.assertEqual(cm.exception.code, 1)
        with open('console-out.txt', 'r') as f:
            self.assertIn("unrecognized key 'options'", f.read())

        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                check_spec(Namespace(config=BFILE))
        with open('console-out.txt', 'r') as f:
            self.assertIn('no unrecognized keys or types', f.read())

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

    Allowed values: ``a``, ``b``, ``c``



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
    # Free-key mapping nodes (value_attributes)
    # ------------------------------------------------------------------

    def _write_freekey_base(self, name='freekey_base.yaml', **extra):
        spec = {
            'attributes': [
                {
                    'name': 'constituents',
                    'type': 'dict',
                    'text': 'constituents keyed by molecule name',
                    'key_text': 'a molecule name',
                    'value_attributes': [
                        {'name': 'smiles', 'type': 'str', 'text': 'SMILES', 'required': True},
                        {'name': 'count', 'type': 'int', 'text': 'how many', 'default': 100},
                    ],
                }
            ]
        }
        spec['attributes'][0].update(extra)
        with open(name, 'w') as f:
            yaml.dump(spec, f)
        return name

    def test_free_keys_accepts_user_chosen_keys(self):
        """Keys under a value_attributes node are the user's own and are not checked."""
        base = self._write_freekey_base()
        Y = Yclept(base, userdict={'constituents': {'STY': {'smiles': 'C=Cc1ccccc1'}}})
        self.assertIn('STY', Y['user']['constituents'])

    def test_free_key_values_get_their_defaults(self):
        """Defaults declared in value_attributes are filled in for every value."""
        base = self._write_freekey_base()
        Y = Yclept(
            base,
            userdict={
                'constituents': {
                    'STY': {'smiles': 'C=Cc1ccccc1'},
                    'GMA': {'smiles': 'CC(=C)C(=O)OCC1CO1', 'count': 50},
                }
            },
        )
        self.assertEqual(Y['user']['constituents']['STY']['count'], 100)
        self.assertEqual(Y['user']['constituents']['GMA']['count'], 50)

    def test_free_key_value_rejects_unknown_attribute(self):
        """A typo *inside* a value is still caught, and the message names the entry."""
        base = self._write_freekey_base()
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'constituents': {'STY': {'smiles': 'C', 'tpyo': 1}}})
        self.assertIn('constituents[STY]', str(cm.exception))
        self.assertIn('smiles', str(cm.exception))

    def test_free_key_value_enforces_required_and_type(self):
        base = self._write_freekey_base()
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={'constituents': {'STY': {'count': 5}}})
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={'constituents': {'STY': {'smiles': 'C', 'count': 'many'}}})

    def test_free_key_value_must_be_a_mapping(self):
        base = self._write_freekey_base()
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'constituents': {'STY': 'not-a-mapping'}})
        self.assertIn("Entry 'STY'", str(cm.exception))

    def test_free_key_node_absent_yields_empty_mapping(self):
        """No keys are invented for a section the user omitted."""
        base = self._write_freekey_base()
        Y = Yclept(base, userdict={})
        self.assertEqual(Y['user']['constituents'], {})

    def test_free_key_node_is_a_branch_in_help(self):
        """A free-key node must not be shown as a leaf, or its values go undocumented."""
        base = self._write_freekey_base()
        Y = Yclept(base)
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help([])
        with open('console-out.txt', 'r') as f:
            self.assertIn('constituents ->', f.read())
        with open('console-out.txt', 'w') as f:
            with redirect_stdout(f):
                Y.console_help(['constituents'])
        with open('console-out.txt', 'r') as f:
            out = f.read()
        self.assertIn('a molecule name', out)
        self.assertIn('smiles', out)

    def test_spec_check_flags_attributes_and_value_attributes_together(self):
        base = yaml.safe_load(
            'attributes:\n'
            '  - name: both\n'
            '    type: dict\n'
            '    text: contradictory\n'
            '    attributes:\n'
            '      - {name: a, type: str, text: a}\n'
            '    value_attributes:\n'
            '      - {name: b, type: str, text: b}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(
            any("declares 'attributes' and 'value_attributes'" in p for p in problems)
        )

    def test_both_child_declarations_raise_at_load(self):
        with open('both_base.yaml', 'w') as f:
            f.write(
                'attributes:\n'
                '  - name: both\n'
                '    type: dict\n'
                '    text: contradictory\n'
                '    attributes:\n'
                '      - {name: a, type: str, text: a, default: x}\n'
                '    value_attributes:\n'
                '      - {name: b, type: str, text: b}\n'
            )
        with self.assertRaises(YclepticError):
            Yclept('both_base.yaml', userdict={})

    def test_spec_check_recurses_into_value_attributes(self):
        """A typo in a value schema is reported, with '[*]' marking the free key."""
        base = yaml.safe_load(
            'attributes:\n'
            '  - name: things\n'
            '    type: dict\n'
            '    text: things\n'
            '    value_attributes:\n'
            '      - {name: color, type: str, text: c, options: [red]}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any('things->[*]->color' in p for p in problems))

    def test_spec_check_flags_key_text_without_value_attributes(self):
        base = yaml.safe_load('attributes:\n  - {name: x, type: dict, text: t, key_text: stray}\n')
        problems = check_base_spec(base)
        self.assertTrue(any("'key_text'" in p for p in problems))

    def test_free_key_defaults_do_not_mutate_the_base_spec(self):
        """Filling per-value defaults must not write back into the schema."""
        spec = {
            'attributes': [
                {
                    'name': 'things',
                    'type': 'dict',
                    'text': 'free-key with a non-empty default',
                    'value_attributes': [
                        {'name': 'size', 'type': 'int', 'text': 'size', 'default': 7}
                    ],
                    'default': {'preset': {}},
                }
            ]
        }
        with open('freekey_mut.yaml', 'w') as f:
            yaml.dump(spec, f)
        Y = Yclept('freekey_mut.yaml', userdict={})
        self.assertEqual(Y['user']['things'], {'preset': {'size': 7}})
        # the schema still says what the file said
        self.assertEqual(Y['base']['attributes'][0]['default'], {'preset': {}})

    def test_free_key_user_values_do_not_mutate_the_base_spec(self):
        """A user's entries must not be merged into the schema's default."""
        spec = {
            'attributes': [
                {
                    'name': 'things',
                    'type': 'dict',
                    'text': 'free-key with a non-empty default',
                    'value_attributes': [
                        {'name': 'size', 'type': 'int', 'text': 'size', 'default': 7}
                    ],
                    'default': {'preset': {}},
                }
            ]
        }
        with open('freekey_mut.yaml', 'w') as f:
            yaml.dump(spec, f)
        Y = Yclept('freekey_mut.yaml', userdict={'things': {'mine': {'size': 3}}})
        self.assertIn('mine', Y['user']['things'])
        self.assertEqual(Y['base']['attributes'][0]['default'], {'preset': {}})

    # ------------------------------------------------------------------
    # value_type: free-key mappings and lists of scalars
    # ------------------------------------------------------------------

    def _write_value_type_base(self, typ='str', container='dict', name='vt_base.yaml'):
        node = {
            'name': 'labels',
            'type': container,
            'text': 'elements of a scalar type',
            'value_type': typ,
        }
        if container == 'dict':
            node['key_text'] = 'a label'
        with open(name, 'w') as f:
            yaml.dump({'attributes': [node]}, f)
        return name

    def test_value_type_mapping_accepts_scalars(self):
        """A free-key mapping of scalars needs no per-value attribute block."""
        base = self._write_value_type_base()
        Y = Yclept(base, userdict={'labels': {'C1': 'carbon', 'N2': 'nitrogen'}})
        self.assertEqual(Y['user']['labels'], {'C1': 'carbon', 'N2': 'nitrogen'})

    def test_value_type_mapping_rejects_wrong_scalar(self):
        base = self._write_value_type_base()
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'labels': {'C1': 3}})
        self.assertIn("Entry 'C1'", str(cm.exception))
        self.assertIn('str', str(cm.exception))

    def test_value_type_str_is_actually_checked(self):
        """str is validated here, unlike a declared str attribute which relies on choices."""
        base = self._write_value_type_base(typ='int')
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={'labels': {'n': 'not-an-int'}})
        Y = Yclept(base, userdict={'labels': {'n': 5}})
        self.assertEqual(Y['user']['labels']['n'], 5)

    def test_value_type_list_checks_every_item(self):
        base = self._write_value_type_base(typ='int', container='list')
        Y = Yclept(base, userdict={'labels': [1, 2, 3]})
        self.assertEqual(Y['user']['labels'], [1, 2, 3])
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'labels': [1, 'two']})
        self.assertIn('Item 1', str(cm.exception))

    def test_spec_check_flags_unknown_value_type(self):
        base = yaml.safe_load(
            'attributes:\n  - {name: m, type: dict, text: t, value_type: string}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any("did you mean 'str'?" in p for p in problems))

    def test_spec_check_flags_key_text_on_a_list(self):
        base = yaml.safe_load(
            'attributes:\n'
            '  - {name: l, type: list, text: t, value_type: str, key_text: stray}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any('positional and have no keys' in p for p in problems))

    def test_spec_check_flags_three_way_declaration(self):
        base = yaml.safe_load(
            'attributes:\n'
            '  - name: m\n'
            '    type: dict\n'
            '    text: t\n'
            '    value_type: str\n'
            '    value_attributes:\n'
            '      - {name: a, type: str, text: a}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any('exactly one way' in p for p in problems))

    # ------------------------------------------------------------------
    # Lists of homogeneous multi-key records
    # ------------------------------------------------------------------

    def _write_record_list_base(self, name='reclist_base.yaml'):
        spec = {
            'attributes': [
                {
                    'name': 'stages',
                    'type': 'list',
                    'text': 'an ordered list of flat records',
                    'value_attributes': [
                        {
                            'name': 'ensemble',
                            'type': 'str',
                            'text': 'the ensemble',
                            'choices': ['nvt', 'npt', 'min'],
                            'required': True,
                        },
                        {'name': 'ps', 'type': 'int', 'text': 'picoseconds', 'default': 100},
                    ],
                }
            ]
        }
        with open(name, 'w') as f:
            yaml.dump(spec, f)
        return name

    def test_record_list_accepts_multi_key_items(self):
        """The shape lwalk's tagged-task idiom cannot express."""
        base = self._write_record_list_base()
        Y = Yclept(base, userdict={'stages': [{'ensemble': 'npt', 'ps': 50}]})
        self.assertEqual(Y['user']['stages'], [{'ensemble': 'npt', 'ps': 50}])

    def test_record_list_fills_per_item_defaults(self):
        base = self._write_record_list_base()
        Y = Yclept(base, userdict={'stages': [{'ensemble': 'npt'}, {'ensemble': 'nvt'}]})
        self.assertEqual([s['ps'] for s in Y['user']['stages']], [100, 100])

    def test_record_list_errors_name_the_index(self):
        base = self._write_record_list_base()
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'stages': [{'ensemble': 'npt'}, {'tpyo': 1}]})
        self.assertIn('stages[1]', str(cm.exception))

    def test_record_list_enforces_required_and_choices(self):
        base = self._write_record_list_base()
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={'stages': [{'ps': 5}]})
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'stages': [{'ensemble': 'bogus'}]})
        # the message names the enclosing item, not the attribute twice over
        self.assertIn("of 'stages[0]'", str(cm.exception))

    def test_record_list_item_must_be_a_mapping(self):
        base = self._write_record_list_base()
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'stages': ['nope']})
        self.assertIn('Item 0', str(cm.exception))

    def test_record_list_defaults_do_not_mutate_the_base_spec(self):
        spec = {
            'attributes': [
                {
                    'name': 'stages',
                    'type': 'list',
                    'text': 'records with a default',
                    'default': [{'ensemble': 'min'}],
                    'value_attributes': [
                        {'name': 'ensemble', 'type': 'str', 'text': 'e'},
                        {'name': 'ps', 'type': 'int', 'text': 'p', 'default': 100},
                    ],
                }
            ]
        }
        with open('reclist_mut.yaml', 'w') as f:
            yaml.dump(spec, f)
        Y = Yclept('reclist_mut.yaml', userdict={})
        self.assertEqual(Y['user']['stages'], [{'ensemble': 'min', 'ps': 100}])
        self.assertEqual(Y['base']['attributes'][0]['default'], [{'ensemble': 'min'}])

    def test_tagged_task_lists_still_work(self):
        """lwalk's idiom is untouched: a list with 'attributes' is still tagged tasks."""
        Y = Yclept(BFILE, userdict={'attribute_2': [{'attribute_2a': {'d2a_val2': 9}}]})
        self.assertEqual(Y['user']['attribute_2'][0]['attribute_2a']['d2a_val2'], 9)

    # ------------------------------------------------------------------
    # list_defaults
    # ------------------------------------------------------------------

    def _write_list_base(self, mode=None, name='listmode_base.yaml'):
        node = {
            'name': 'ladder',
            'type': 'list',
            'text': 'the equilibration ladder',
            'default': ['min', 'nvt', 'npt'],
        }
        if mode is not None:
            node['list_defaults'] = mode
        with open(name, 'w') as f:
            yaml.dump({'attributes': [node]}, f)
        return name

    def test_list_defaults_append_is_the_default(self):
        """Historical behavior is preserved for schemas that declare nothing."""
        base = self._write_list_base()
        Y = Yclept(base, userdict={'ladder': ['nvt']})
        self.assertEqual(Y['user']['ladder'], ['min', 'nvt', 'npt', 'nvt'])

    def test_list_defaults_replace_honors_the_user_list(self):
        base = self._write_list_base(mode='replace')
        Y = Yclept(base, userdict={'ladder': ['nvt']})
        self.assertEqual(Y['user']['ladder'], ['nvt'])

    def test_list_defaults_replace_still_supplies_default_when_absent(self):
        base = self._write_list_base(mode='replace')
        Y = Yclept(base, userdict={})
        self.assertEqual(Y['user']['ladder'], ['min', 'nvt', 'npt'])

    def test_list_defaults_explicit_append_matches_the_default(self):
        base = self._write_list_base(mode='append')
        Y = Yclept(base, userdict={'ladder': ['nvt']})
        self.assertEqual(Y['user']['ladder'], ['min', 'nvt', 'npt', 'nvt'])

    def test_list_defaults_unrecognized_mode_raises(self):
        base = self._write_list_base(mode='overwrite')
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={'ladder': ['nvt']})
        self.assertIn('list_defaults', str(cm.exception))

    def test_spec_check_flags_bad_list_defaults(self):
        base = yaml.safe_load(
            'attributes:\n'
            '  - {name: l, type: list, text: t, default: [a], list_defaults: overwrite}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any("did you mean 'replace'?" in p for p in problems))

    def test_spec_check_flags_list_defaults_on_a_task_list(self):
        """A list with 'attributes' goes through lwalk, which never merges defaults."""
        base = yaml.safe_load(
            'attributes:\n'
            '  - name: tasks\n'
            '    type: list\n'
            '    text: an ordered task list\n'
            '    list_defaults: replace\n'
            '    attributes:\n'
            '      - {name: md, type: dict, text: a task}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any('ordered sequence of tasks' in p for p in problems))

    def test_spec_check_flags_list_defaults_on_non_list(self):
        base = yaml.safe_load(
            'attributes:\n  - {name: s, type: str, text: t, list_defaults: replace}\n'
        )
        problems = check_base_spec(base)
        self.assertTrue(any("applies only to 'list'" in p for p in problems))

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
    # Defaults are handed out as copies, never as the schema's own objects
    # ------------------------------------------------------------------

    def _write_alias_base(self, name='alias_base.yaml'):
        spec = {
            'attributes': [
                {
                    'name': 'opts',
                    'type': 'dict',
                    'text': 'a bare dict with a default',
                    'default': {'cores': 4},
                },
                {
                    'name': 'files',
                    'type': 'list',
                    'text': 'a plain list with a default',
                    'default': ['a.dat', 'b.dat'],
                },
            ]
        }
        with open(name, 'w') as f:
            yaml.dump(spec, f)
        return name

    def test_loading_a_config_does_not_rewrite_the_schema(self):
        """special_update writes into its first argument; it must not be the spec's."""
        base = self._write_alias_base()
        Y = Yclept(base, userdict={'opts': {'threads': 8}})
        self.assertEqual(Y['user']['opts'], {'cores': 4, 'threads': 8})
        self.assertEqual(Y['base']['attributes'][0]['default'], {'cores': 4})

    def test_absent_list_default_is_not_handed_out_by_reference(self):
        """Consumer code mutating its own config must not grow the schema's default."""
        base = self._write_alias_base()
        Y = Yclept(base, userdict={})
        self.assertIsNot(Y['user']['files'], Y['base']['attributes'][1]['default'])
        Y['user']['files'].append('c.dat')
        self.assertEqual(Y['base']['attributes'][1]['default'], ['a.dat', 'b.dat'])

    def test_absent_dict_default_is_not_handed_out_by_reference(self):
        base = self._write_alias_base()
        Y = Yclept(base, userdict={})
        self.assertIsNot(Y['user']['opts'], Y['base']['attributes'][0]['default'])
        Y['user']['opts']['scratch'] = True
        self.assertEqual(Y['base']['attributes'][0]['default'], {'cores': 4})

    def test_make_default_specs_reports_the_schema_not_the_user(self):
        """The method's whole job is to answer what the defaults are."""
        base = self._write_alias_base()
        Y = Yclept(base, userdict={'opts': {'threads': 8}})
        self.assertEqual(Y.make_default_specs('opts'), {'opts': {'cores': 4}})

    def test_make_default_specs_result_is_safe_to_mutate(self):
        base = self._write_alias_base()
        Y = Yclept(base)
        got = Y.make_default_specs('files')
        got['files'].append('MUTATED')
        self.assertEqual(Y['base']['attributes'][1]['default'], ['a.dat', 'b.dat'])

    def test_repeated_update_user_does_not_accumulate_in_the_schema(self):
        base = self._write_alias_base()
        Y = Yclept(base, userdict={'opts': {'threads': 8}})
        Y.update_user({'opts': {'debug': True}})
        self.assertEqual(Y['base']['attributes'][0]['default'], {'cores': 4})
        # update_user is a top-level dict.update, so passing 'opts' replaces its
        # value entirely and 'threads' is gone.  It used to survive that
        # replacement only because it had been merged into the schema's default.
        self.assertEqual(Y['user']['opts'], {'cores': 4, 'debug': True})

    def test_update_user_leaves_unmentioned_attributes_alone(self):
        """The boundary of the change above: only the replaced attribute is affected."""
        base = self._write_alias_base()
        Y = Yclept(base, userdict={'opts': {'threads': 8}})
        Y.update_user({'files': ['z.dat']})
        self.assertEqual(Y['user']['opts'], {'cores': 4, 'threads': 8})

    # ------------------------------------------------------------------
    # required on containers
    # ------------------------------------------------------------------

    def _write_required_base(self, node, name='required_base.yaml'):
        with open(name, 'w') as f:
            yaml.dump({'attributes': [node]}, f)
        return name

    def test_required_list_with_nothing_to_fill_it_raises(self):
        """A required list used to be silently satisfied with []."""
        base = self._write_required_base(
            {'name': 'a', 'type': 'list', 'text': 'a required list', 'required': True}
        )
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={})
        self.assertIn('requires a value', str(cm.exception))

    def test_required_childless_dict_with_nothing_to_fill_it_raises(self):
        base = self._write_required_base(
            {'name': 'a', 'type': 'dict', 'text': 'a required bare dict', 'required': True}
        )
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={})

    def test_required_container_with_a_default_uses_it(self):
        """A default supplies the value, exactly as it does for a scalar."""
        base = self._write_required_base(
            {
                'name': 'a',
                'type': 'list',
                'text': 'a required list with a default',
                'required': True,
                'default': ['x'],
            }
        )
        Y = Yclept(base, userdict={})
        self.assertEqual(Y['user']['a'], ['x'])

    def test_required_dict_with_attributes_is_synthesized_not_refused(self):
        """Its children supply the block, and their own required flags then apply."""
        base = self._write_required_base(
            {
                'name': 'a',
                'type': 'dict',
                'text': 'a required block',
                'required': True,
                'attributes': [{'name': 'n', 'type': 'int', 'text': 'n', 'default': 1}],
            }
        )
        Y = Yclept(base, userdict={})
        self.assertEqual(Y['user']['a'], {'n': 1})

    def test_required_parent_dicts_nest_without_their_own_defaults(self):
        """pestifer's shape: required dicts nested two deep, none with a default,
        satisfied only by descent to a leaf that has one.  Binding required on a
        parent would fail every config that omits the block."""
        base = self._write_required_base(
            {
                'name': 'charmmff',
                'type': 'dict',
                'text': 'outer required block, no default',
                'required': True,
                'attributes': [
                    {
                        'name': 'standard',
                        'type': 'dict',
                        'text': 'inner required block, no default',
                        'required': True,
                        'attributes': [
                            {
                                'name': 'rtf',
                                'type': 'list',
                                'text': 'required list, but it has a default',
                                'required': True,
                                'default': ['top_all36_prot.rtf'],
                            }
                        ],
                    }
                ],
            }
        )
        Y = Yclept(base, userdict={})
        self.assertEqual(
            Y['user']['charmmff'], {'standard': {'rtf': ['top_all36_prot.rtf']}}
        )

    def test_required_parent_dict_still_raises_via_a_bare_required_child(self):
        """Descent is not a blanket exemption: the child's own required still binds."""
        base = self._write_required_base(
            {
                'name': 'outer',
                'type': 'dict',
                'text': 'required block, no default',
                'required': True,
                'attributes': [
                    {
                        'name': 'inner',
                        'type': 'list',
                        'text': 'required list with nothing to fill it',
                        'required': True,
                    }
                ],
            }
        )
        with self.assertRaises(YclepticError) as cm:
            Yclept(base, userdict={})
        self.assertIn("'inner'", str(cm.exception))

    def test_required_false_container_is_still_skipped(self):
        base = self._write_required_base(
            {'name': 'a', 'type': 'list', 'text': 'opt-out', 'required': False}
        )
        Y = Yclept(base, userdict={})
        self.assertNotIn('a', Y['user'])

    def test_required_free_key_mapping_raises_when_absent(self):
        """Keys are the user's to invent, so nothing can synthesize the mapping."""
        base = self._write_required_base(
            {
                'name': 'a',
                'type': 'dict',
                'text': 'a required free-key mapping',
                'required': True,
                'value_attributes': [{'name': 'x', 'type': 'str', 'text': 'x'}],
            }
        )
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={})

    def test_required_tagged_task_list_raises_when_absent(self):
        """'attributes' on a list names possible items; an empty list holds none."""
        base = self._write_required_base(
            {
                'name': 'a',
                'type': 'list',
                'text': 'a required task list',
                'required': True,
                'attributes': [{'name': 'md', 'type': 'dict', 'text': 'a task'}],
            }
        )
        with self.assertRaises(YclepticError):
            Yclept(base, userdict={})

    def test_required_container_satisfied_by_the_user_does_not_raise(self):
        base = self._write_required_base(
            {'name': 'a', 'type': 'list', 'text': 'a required list', 'required': True}
        )
        Y = Yclept(base, userdict={'a': ['given']})
        self.assertEqual(Y['user']['a'], ['given'])

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
