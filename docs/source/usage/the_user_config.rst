.. _usage_the_user_config:

The User Configuration
========================

The base config specifies both the allowable syntax of a user config and how the resulting dictionary representation in memory should look.  Every directive name is a key in the user config.  So an example user config that conforms to the base config shown in :ref:`usage_the_base_config` might look like

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