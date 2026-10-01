.. _usage_yclept_check_spec:

``yclept check-spec``
=====================

A base config is data, and ycleptic reads only the keys it recognizes.  A
misspelled key or type name is therefore discarded without comment, leaving you
with a declaration that quietly does nothing.  The classic case is writing
``options:`` where ycleptic expects ``choices:``: the attribute looks
constrained, but every value is accepted.

``yclept check-spec`` reads a base config file and reports every such
declaration, and every declaration whose shape is wrong:

.. code-block:: console

   $ yclept check-spec base.yaml
   base config base.yaml has 3 declarations ycleptic does not act on:
     - attribute 'fetch->source': unrecognized key 'options' (did you mean 'choices'?); it is ignored
     - attribute 'fetch->format': unrecognized type 'string' (did you mean 'str'?); the attribute is left unvalidated
     - attribute 'run->nsteps': 'choices' is only enforced on 'str' attributes, and this one is 'int'; the allowed values are not applied

It exits ``0`` when the spec is clean and ``1`` when anything is reported, so it
can gate a CI run:

.. code-block:: yaml

   - name: Check the base config spec
     run: yclept check-spec mypackage/data/base.yaml

.. tip::

   If you gate on this from your own test suite rather than from CI, pair the
   check with a **negative control** --- a test that re-introduces a known
   mistake in memory and requires a complaint about it:

   .. code-block:: python

      def test_shipped_schema_is_clean():
          assert check_base_spec(yaml.safe_load(open(SCHEMA))) == []

      def test_the_checker_is_actually_running():
          bad = yaml.safe_load(open(SCHEMA))
          bad['attributes'].append('not-an-attribute')
          assert check_base_spec(bad) != []

   The first test alone proves very little. A dependency floor such as
   ``ycleptic>=2.4.3`` is satisfied the moment the installed version is new
   enough, so a clean schema passes against an *older* ycleptic that never ran
   the check you are relying on --- and the suite stays green while the
   guarantee is gone. The second test fails in that case, which is the point of
   it.

What it looks for
-----------------

1. Keys in an attribute node outside the recognized set (``name``, ``type``,
   ``text``, ``default``, ``required``, ``choices``, ``case_sensitive``,
   ``attributes``, ``docs``), and keys in a ``docs`` block outside ``title``,
   ``text``, and ``example``.
2. ``type`` values outside ``str``, ``int``, ``float``, ``bool``, ``tuple``,
   ``list``, and ``dict``.  An unrecognized type name matches no branch of the
   validator, so the attribute gets no handling at all --- including its
   ``choices``, even when ``choices`` is spelled correctly, and including its
   ``default``, which is never applied.
3. Attributes with no ``type`` at all.
4. ``choices`` on an attribute whose type is not ``str``.  Allowed values are
   currently enforced only for strings, so elsewhere the list has no effect.
5. Declarations whose *shape* is wrong even though every key and type name is
   recognized --- see below.

Where a suggestion is obvious, it is offered: ``options`` for ``choices``,
``string`` for ``str``, and so on.

Shape, not just vocabulary
--------------------------

A base config can use nothing but recognized keys and still describe the wrong
thing.  The one worth knowing about is an indentation slip, because the result
is valid YAML that quietly loses an attribute.

Attribute entries and the items of a ``default`` list sit at different depths.
Writing a new attribute one level too deep puts it *inside the previous
attribute's default* rather than beside it:

.. code-block:: yaml

   - name: str
     type: list
     default:
       - toppar_all36_moreions.str
       - name: prm            # meant to be a sibling attribute, one level out
         type: list
         default:
           - dihedral_fills.prm

Nothing about that is unrecognized, so for a long time ``check-spec`` passed it.
The cost is paid twice over: ``prm`` ceases to exist, so a user config setting
it is ignored and its defaults are never applied, and ``str`` gains a mapping
among its filenames.  ``check-spec`` now reports it:

.. code-block:: console

   - attribute 'charmmff->custom->str': its 'default' contains what looks like the
     attribute 'prm' rather than a value; an attribute indented one level too deep is
     swallowed into the previous attribute's default, and then declares nothing

The test is deliberately narrow --- a mapping with a ``name`` *and* a ``type``
naming one of ycleptic's own types --- so ordinary data in a ``default`` is left
alone.

Two related checks come with it:

- a ``default`` that contradicts its ``type``, such as ``type: list`` with a
  string default.  ``default:`` with nothing after it is YAML ``null``, which is
  how a schema ordinarily says "declared, but with no value", and is not
  reported;
- an ``attributes`` or ``value_attributes`` entry that is not an attribute at
  all, or that has no ``name``.  Every walker in ycleptic skips such an entry,
  so whatever it was meant to declare does not exist.

Checking from Python
--------------------

The same checks run whenever a :class:`~ycleptic.yclept.Yclept` is constructed.
By default anything found is reported as a
:class:`~ycleptic.errors.YclepticSpecWarning` and the config still loads, so an
existing schema keeps working while you clean it up:

.. code-block:: python

   Y = Yclept('base.yaml', userfile='user.yaml')
   # YclepticSpecWarning: base config base.yaml has 1 declaration ycleptic does not act on:
   #   - attribute 'fetch->source': unrecognized key 'options' (did you mean 'choices'?); it is ignored

Pass ``strict_spec=True`` to make it an error instead:

.. code-block:: python

   Y = Yclept('base.yaml', userfile='user.yaml', strict_spec=True)
   # raises YclepticError

:func:`ycleptic.speccheck.check_base_spec` returns the same findings as a list
of strings if you would rather handle them yourself.
