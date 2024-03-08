Usage
=====

Installation of Ycleptic gives access to the ``Yclept`` class.

``ycleptic`` is meant to be used inside any Python package where the developer
wants to specify the allowed formats, expected values, default values, required
values, etc., of a YAML-format user input file (a "configuration").

To use ``ycleptic`` in your package, you should create a "base" configuration file for ``ycleptic`` that lives in your package as package data.  More about that file in a moment.

You then might like to create a "config" class for your package that is a descendant
of ``Yclept``, and initialize it with your base config and a user config. For example:

.. code-block:: python

  from ycleptic.yclept import Yclept
  from mypackage import data

  class MyConfig(Yclept):
    def __init__(self, userconfigfile=''):
        basefile=os.path.join(os.path.dirname(data.__file__),"base.yaml")
        super().__init__(data.basefile,userconfigfile=userconfigfile)


Here, ``data`` is just a directory where you store your package data (``rootdir/mypackage/data``, for example), and you can put ``base.yaml`` in that directory as the "base" configuration description.  Essentially, it is a description of *what* can be configured by a *user's* configuration file when *they* run your package.  Now, inside your package source, if you want to read in the user's configuration file (like if its name was passed in as a command-line argument), you would instantiate a member of the ``MyConfig`` class:

.. code-block:: python

  c = MyConfig(userconfigfile=args.c)

I imagine this might conform to a command-line invocation like:

.. code-block:: console

  $ mypackagecommand -c myconfig.yaml


The Base Config
---------------

The heart of ``ycleptic`` is the base configuration file, which the developer must write. The base configuration is the developer's expression of what a *user* can configure when they run the package.  Below is an example:

.. code-block:: yaml

  directives:
    - name: directive_1
      type: dict
      text: This is a description of Directive 1
      directives:
        - name: directive_1_1
          type: list
          text: This is a description of Directive 1.1
          default:
            - 1
            - 2
            - 3
        - name: directive_1_2
          type: str
          text: This is a description of Directive 1.2
          options: [ValA, ValB]
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
              default: 1.0
            - name: d2a_val2
              type: int
              text: An int for Value 2 of Directive 2a
              default: 6
            - name: d2_a_dict
              type: dict
              text: this is a dict
              default:
                a: 123
                b: 567
                c: 987
        - name: directive_2b
          type: dict
          text: Directive 2b is another possible directive
          directives:
            - name: val1
              type: str
              text: Val 1 of D2b
              default: a_nice_value
            - name: val2
              type: str
              text: Val 2 of D2b
              default: a_not_so_nice_value
    - name: directive_3
      type: dict
      text: Directive 3 has a lot of nesting
      directives:
        - name: directive_3_1
          type: dict
          text: This is a description of Directive 3.1
          directives:
            - name: directive_3_1_1
              type: dict
              text: This is a description of Directive 3.1.1
              directives:
                - name: directive_3_1_1_1
                  type: dict
                  text: This is a description of Directive 3.1.1.1
                  directives:
                    - name: d3111v1
                      type: str
                      text: Value 1 of D 3.1.1.1
                      default: ABC
                    - name: d3111v2
                      type: float
                      text: Value 2 of D 3.1.1.1
                      required: False
        - name: directive_3_2
          type: dict
          text: This is a description of Directive 3.2
          directives:
            - name: d322
              type: list
              text: Directive 3.2.2 has a list of possible subdirectives
              directives:
                - name: d322a
                  type: dict
                  text: D 3.2.2a executes a series of flips
                  directives:
                    - name: nflips
                      type: int
                      text: Number of flips
                      default: 0
                    - name: flipaxis
                      type: str
                      text: Axis around which flip is performed
                      options: ['x','y','z']
                - name: d322b
                  type: dict
                  text: Subdirective D 3.2.2b saves the result
                  directives:
                    - name: filename
                      type: str
                      text: name of file to save
                      default: flipfile.dat


The base config must open with the single identifier ``directives``, under which is a list of one or more top-level directives.  A directive is a dictionary with keys ``name``, ``type``, and ``text``, and then data content.

``type`` can be one of ``int``, ``float``, ``str``, ``bool``, ``list``, or ``dict``.  The data content in a directive is of type ``type`` unless two conditions are met:

1. ``type`` is either ``list`` or ``dict``; and
2. the keyword ``directives`` is present.

In this case, there are subdirectives.  If the ``type`` was ``dict``, then the subdirectives are children of the parent directive and all operate at the same level.  If the ``type`` was ``list``, then the subdirectives defined are expected to be ordered as a list of tasks that the parent directive executes in the order they appear in the user's config file.  In the base file, both are entered as lists of directives.

``text`` is just meant for helpful text describing the directive, and it can be completely free-form as long as it is on one line.

There are three other keys that a directive may have:

1. ``default``: as you might expect, this are default values to assign to the directive if the user "declares" the directive but does not provide it any values.
2. ``required``:  a boolean.  If False, that means no defaults are assigned; if a user declares this directive without providing values, an error occurs, but a user need not declare this directive at all.  If True, the directive must be declared (and if it is nested, all the antecedant directives must also be declared).
3. ``options``: a list of allowed values; if the user declares this directive with a value not in this list, an error occurs.

Console Help
------------

The ``Yclept`` class has a method called ``console_help`` that is meant to provide interactive help to a package user trying to develop their own config file that conform's to your package's base config.  

Suppose this is the content of ``config.py``:

.. code-block:: python

  from ycleptic.yclept import Yclept
  from mypackage import data

  class MyConfig(Yclept):
    def __init__(self, userconfigfile=''):
        basefile=os.path.join(os.path.dirname(data.__file__),"base.yaml")
        super().__init__(data.basefile,userconfigfile=userconfigfile)
   

Here is an example of how the interactive help works:

.. code-block:: python

  >>> from mypackage import MyConfig
  >>> c=MyConfig()
  >>> c.console_help()
      Help available for directive_1, directive_2, directive_3

This reflects the fact that the three top-level directives available are called ``directive_1``, ``directive_2``, and ``directive_3``, respectively.  To drill down, you just add the directive names:

.. code-block:: python

  >>> c.console_help('directive_1')
  directive_1:
    This is a description of Directive 1
    type: dict
    Help available for directive_1_1, directive_1_2
  >>> c.console_help('directive_1','directive_1_2')
  directive_1->
  directive_1_2:
    This is a description of Directive 1.2
    type: str

In this way, you can interactively explore the whole structure of the base config, and learn how to write a user config.

The User Config
---------------

The base config specifies both the allowable syntax of a user config and how the resulting dictionary representation in memory should look.  Every directive name is a key in the user config.  So an example user config that conforms to the base config above might look like

.. code-block:: yaml

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

Here, the user has declared an instance of ``directive_2`` as a list of "tasks": first, an instance of ``directive_2b`` with certain values of ``val1`` and ``val2``, then ``directive_2a``, and then another different instance of ``directive_2b``.  The declaration of ``directive_1`` with its one subdirective appears below ``directive_2``, but they are not in any kind of sequence as far as the interpreter goes, since they are dictionary keys, not list elements.

The subdirective ``d2_a_dict`` of ``directive_2a`` reassigns values for keys ``b`` and ``c``; the default value for key ``a`` claimed in ``base.yaml`` (123) is unchanged.

The Resource File
-----------------

You may want users of your application to be able to set their own global default values for directives, overwriting defaults you define in your application's base configuration.  ``Yclept`` supports reading a secondary resource file (e.g., ``~/.your_app_name.rc``) in which users can specify directives that replace or add to the list of directives in your application's base configuration.

For example, continuing with the base configuration defined above, suppose a user of your application has the file ``~/.your_app_name.rc`` with these contents:

.. code-block:: yaml

  directives:
    - name: directive_2
      type: list
      text: Directive 2 is interpretable as an ordered list of directives
      directives:
        - name: directive_2a
          type: dict
          text: Directive 2a is one possible directive in a user's list
          directives:
            - name: d2a_val2
              type: int
              text: An int for Value 2 of Directive 2a
              default: 7 # user has changed this in their resource file

The presence of this file indicates the user would like the default value of directive ``d2a_val2`` under directive ``directive_2a`` of base directive ``directive_2`` to be 7 instead of 6.