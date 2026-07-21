.. _usage_quickstart:

Quickstart
==========

This is the smallest useful Ycleptic setup: define a base config, load a user
config against it, and generate documentation — all from one schema file.

1. Write a base config
-----------------------------

The base config is a YAML file describing what your users may configure.  Ship
it as package data, e.g. ``mypackage/data/base.yaml``:

.. code-block:: yaml

  attributes:
    - name: temperature
      type: float
      text: Simulation temperature in kelvin
      default: 300.0
    - name: integrator
      type: str
      text: Integration scheme to use
      choices: [verlet, langevin]
      default: verlet

2. Load a user config
-----------------------------

Read the base config together with a user's config through
:class:`ycleptic.yclept.Yclept`.  Omitted values are filled in from their
declared defaults; invalid values raise :class:`ycleptic.YclepticError`:

.. code-block:: python

  from ycleptic import Yclept, YclepticError

  try:
      config = Yclept(basefile='mypackage/data/base.yaml', userfile='user.yaml')
  except YclepticError as e:
      raise SystemExit(f'Invalid configuration: {e}')

  print(config['user']['temperature'])   # 300.0 if the user omitted it

If ``user.yaml`` sets only the integrator:

.. code-block:: yaml

  integrator: langevin

then ``config['user']`` becomes ``{'integrator': 'langevin', 'temperature':
300.0}`` — the default temperature is supplied automatically.

3. Generate documentation and explore
--------------------------------------------

From the *same* base config you can generate a Sphinx reference tree:

.. code-block:: console

  $ yclept make-doc mypackage/data/base.yaml --root docs/source/config_ref

and let your users explore the configuration interactively:

.. code-block:: console

  $ yclept config-help mypackage/data/base.yaml

The rest of this guide covers each piece in detail: :ref:`usage_the_base_config`,
:ref:`usage_the_user_config`, :ref:`usage_interactive_help`, and
:ref:`usage_yclept_makedoc`.
