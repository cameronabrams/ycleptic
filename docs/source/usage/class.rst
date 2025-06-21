.. _usage_class:

``Yclept`` Class
====================

Installation of Ycleptic gives access to the ``Yclept`` class.

``Yclept`` is meant to be used inside any Python package where the developer
wants to specify the allowed formats, expected values, default values, required
values, etc., of a YAML-format configuration file for the developer's app.

To use ``ycleptic`` in your app, you should create a "base" configuration file for ``ycleptic`` that lives in your app as package data.  For example, suppose your app is constructed like this:

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

``base.yaml`` could be your base configuration file. More about that file in a moment.

You then might like to create a "config" class for your package that inherits ``Yclept``, and initialize it with your base config and a user config. For example:

.. code-block:: python

  from ycleptic.yclept import Yclept
  from mypackage import data

  class MyConfig(Yclept):
    def __init__(self, userconfigfile=''):
        basefile=os.path.join(os.path.dirname(data.__file__),"base.yaml")
        super().__init__(data.basefile,userconfigfile=userconfigfile)


Here, ``data`` is just a directory where you store your package data (``rootdir/mypackage/data``, in the example), and you can put ``base.yaml`` in that directory as the "base" configuration description.  Essentially, it is a description of **what** can be configured by a **user's** configuration file when **they** run your app.  Now, inside your app source, if you want to read in the user's configuration file (like if its name was passed in as a command-line argument), you would instantiate a member of the ``MyConfig`` class:

.. code-block:: python

  c = MyConfig(userconfigfile=args.c)

This assumes you are using ``argparse`` in the canonical way.  A user might run your app at the command-line like this:

.. code-block:: console

  $ mypackagecommand -c myconfig.yaml
