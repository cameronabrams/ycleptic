.. _usage_class:

``Yclept`` Class
====================

Installation of Ycleptic gives access to the :class:`ycleptic.yclept.Yclept` class.

The :class:`ycleptic.yclept.Yclept` class is meant to be used inside any Python package where the developer
wants to specify the allowed formats, expected values, default values, required
values, etc., of a YAML-format configuration file for the developer's app.

To use ``ycleptic`` in your app, you must create a base configuration file that lives in your app as package data.  For example, suppose your app is constructed like this:

.. code-block:: text

   rootdir
   ├── mypackage/
   │   ├── config.py
   │   ├── data/
   │   │   ├── base.yaml
   │   │   └── __init__.py
   │   ├── docs/
   │   │   └── source/
   │   │       └── intro.rst
   │   ├── __init__.py
   │   └── otherstuff/
   │       └── stuff.py
   ├── README.md
   └── setup.py

``base.yaml`` is a base configuration file. More about that file in a moment.

You then might like to create a "config" class for your package that inherits :class:`ycleptic.yclept.Yclept`, and initialize it with your base config and a user config. For example:

.. code-block:: python

  from ycleptic.yclept import Yclept
  from mypackage import data # to get the path to your package data; there are other ways to do this

  class MyConfig(Yclept):
    def __init__(self, userconfigfile=''):
        basefile=os.path.join(os.path.dirname(data.__file__),"base.yaml")  # your app's base config
        super().__init__(data.basefile,userconfigfile=userconfigfile)


Here, ``data`` is just a directory where you store your package data (``rootdir/mypackage/data``, in the example), and you can put ``base.yaml`` in that directory as the base configuration description.  Essentially, it is a description of **what** can be configured by a **user's** configuration file when **they** run your app.  Now, inside your app source, if you want to read in the user's configuration file (like if its name was passed in as a command-line argument), you would instantiate a member of the ``MyConfig`` class:

.. code-block:: python

  c = MyConfig(userconfigfile=args.c)

This assumes you are using ``argparse`` in the canonical way.  A user might run your app at the command-line like this:

.. code-block:: console

  $ mypackagecli -c user_config.yaml

Handling configuration errors
-----------------------------

When a user configuration is invalid — an unknown attribute, a missing required
value, a value outside the allowed ``choices``, or a value of the wrong type —
:class:`ycleptic.yclept.Yclept` raises :class:`ycleptic.YclepticError`.  The
command-line interface catches this exception and prints a clean, traceback-free
message before exiting.  An application that embeds ``Yclept`` can catch it
directly instead of having the interpreter terminated:

.. code-block:: python

  from ycleptic import Yclept, YclepticError

  try:
      c = MyConfig(userconfigfile=args.c)
  except YclepticError as e:
      print(f'Invalid configuration: {e}')
      raise SystemExit(1)

``YclepticError`` is re-exported from the top level, so ``from ycleptic import
YclepticError`` is the stable, supported import path.

.. autoexception:: ycleptic.YclepticError
   :show-inheritance:
   :no-index:
