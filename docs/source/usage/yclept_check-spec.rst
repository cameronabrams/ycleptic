.. _usage_yclept_check_spec:

``yclept check-spec``
=====================

A base config is data, and ycleptic reads only the keys it recognizes.  A
misspelled key or type name is therefore discarded without comment, leaving you
with a declaration that quietly does nothing.  The classic case is writing
``options:`` where ycleptic expects ``choices:``: the attribute looks
constrained, but every value is accepted.

``yclept check-spec`` reads a base config file and reports every such
declaration:

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

Where a suggestion is obvious, it is offered: ``options`` for ``choices``,
``string`` for ``str``, and so on.

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
