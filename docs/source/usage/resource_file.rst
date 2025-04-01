.. _usage_resource_file:

Resource File
==================

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