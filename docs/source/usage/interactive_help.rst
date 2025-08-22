.. _usage_interactive_help:

Interactive Help
===================

The ``Yclept`` class has a method called ``console_help()`` that is meant to provides interactive help to a package user trying to develop their own config file that conform's to your package's base config.  

Suppose this is the content of ``config.py``:

.. code-block:: python

  from ycleptic.yclept import Yclept
  from mypackage import data

  class MyConfig(Yclept):
    def __init__(self, userconfigfile=''):
        basefile=os.path.join(os.path.dirname(data.__file__),"base.yaml")
        super().__init__(data.basefile,userconfigfile=userconfigfile)
   

Here is an example of how the interactive help works:

.. code-block:: console

  >>> from mypackage import MyConfig
  >>> c=MyConfig()
  >>> c.console_help([],interactive_prompt='help: ')
      attribute_1 ->
      attribute_2 ->
      attribute_3 ->
      .. up
      ! quit
  help: 

This reflects the fact that the three top-level attributes available are called ``attribute_1``, ``attribute_2``, and ``attribute_3``, respectively.  To drill down, you just type one of the choices at the prompt:

.. code-block:: console

    >>> Y.console_help([],interactive_prompt='help: ')
        attribute_1 ->
        attribute_2 ->
        attribute_3 ->
        .. up
        ! quit
    help: attribute_1

    attribute_1:
        This is a description of Directive 1

    base|attribute_1
        attribute_1_1
        attribute_1_2
        .. up
        ! quit
    help: 


In this way, you can interactively explore the whole structure of the base config, and learn how to write a user config.
