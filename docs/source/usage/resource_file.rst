.. _usage_resource_file:

Resource File
==================

You may want users of your application to be able to set their own global default values for attributes, overwriting defaults you define in your application's base configuration.  ``Yclept`` supports reading a secondary resource file (e.g., ``~/.your_app_name.rc``) in which users can specify attributes that replace or add to the list of attributes in your application's base configuration.

For example, continuing with the base configuration defined above, suppose a user of your application has the file ``~/.your_app_name.rc`` with these contents:

.. code-block:: yaml

  attributes:
    - name: attribute_2
      type: list
      text: Directive 2 is interpretable as an ordered list of attributes
      attributes:
        - name: attribute_2a
          type: dict
          text: Directive 2a is one possible attribute in a user's list
          attributes:
            - name: d2a_val2
              type: int
              text: An int for Value 2 of Directive 2a
              default: 7 # user has changed this in their resource file

The presence of this file indicates the user would like the default value of attribute ``d2a_val2`` under attribute ``attribute_2a`` of base attribute ``attribute_2`` to be 7 instead of 6.