.. _usage_the_base_config:

The Base Configuration
========================

The heart of ``ycleptic`` is the base configuration file, which the app developer must write. The base configuration is the developer's expression of what a *user* can configure when they run the developer's app.  Below is an example:

.. code-block:: yaml

  attributes:
    - name: attribute_1
      type: dict
      text: This is a description of Attribute 1
      attributes:
        - name: attribute_1_1
          type: list
          text: This is a description of Attribute 1.1
          default:
            - 1
            - 2
            - 3
        - name: attribute_1_2
          type: str
          text: This is a description of Attribute 1.2
          choices: [valA, valB]
    - name: attribute_2
      type: list
      text: Attribute 2 is interpretable as an ordered list of attributes
      attributes:
        - name: attribute_2a
          type: dict
          text: Attribute 2a is one possible attribute in a user's list
          attributes:
            - name: d2a_val1
              type: float
              text: A floating point value for Value 1 of Attribute 2a
              default: 1.0
            - name: d2a_val2
              type: int
              text: An int for Value 2 of Attribute 2a
              default: 6
            - name: d2_a_dict
              type: dict
              text: this is a dict
              default:
                a: 123
                b: 567
                c: 987
        - name: attribute_2b
          type: dict
          text: Attribute 2b is another possible attribute
          attributes:
            - name: val1
              type: str
              text: Val 1 of D2b
              default: a_nice_value
            - name: val2
              type: str
              text: Val 2 of D2b
              default: a_not_so_nice_value
    - name: attribute_3
      type: dict
      text: Attribute 3 has a lot of nesting
      attributes:
        - name: attribute_3_1
          type: dict
          text: This is a description of Attribute 3.1
          attributes:
            - name: attribute_3_1_1
              type: dict
              text: This is a description of Attribute 3.1.1
              attributes:
                - name: attribute_3_1_1_1
                  type: dict
                  text: This is a description of Attribute 3.1.1.1
                  attributes:
                    - name: d3111v1
                      type: str
                      text: Value 1 of D 3.1.1.1
                      default: ABC
                    - name: d3111v2
                      type: float
                      text: Value 2 of D 3.1.1.1
                      required: False
        - name: attribute_3_2
          type: dict
          text: This is a description of Attribute 3.2
          attributes:
            - name: d322
              type: list
              text: Attribute 3.2.2 has a list of possible subattributes
              attributes:
                - name: d322a
                  type: dict
                  text: D 3.2.2a executes a series of flips
                  attributes:
                    - name: nflips
                      type: int
                      text: Number of flips
                      default: 0
                    - name: flipaxis
                      type: str
                      text: Axis around which flip is performed
                      choices: ['x','y','z']
                - name: d322b
                  type: dict
                  text: Subattribute D 3.2.2b saves the result
                  attributes:
                    - name: filename
                      type: str
                      text: name of file to save
                      default: flipfile.dat


The base config must open with the single identifier ``attributes``, under which is a list of one or more top-level attributes.  Every attribute must have a declared type, and attributes can be nested.

``type`` can be one of ``int``, ``float``, ``str``, ``bool``, ``tuple``, ``list``, or ``dict``.  The data content in an attribute is of type ``type`` unless two conditions are met:

1. ``type`` is either ``list`` or ``dict``; and
2. the keyword ``attributes`` is present.

In this case, there are subattributes.  If the ``type`` was ``dict``, then the subattributes are children of the parent attribute and all operate at the same level.  If the ``type`` was ``list``, then the subattributes defined are expected to be ordered as a list of tasks that the parent attribute executes in the order they appear in the user's config file.  In the base file, both are entered as lists of attributes.

``text`` is just meant for helpful text describing the attribute, and it can be completely free-form as long as it is on one line or blocked multiline using ``|``.

There are several other keys an attribute may have:

1. ``default``: the default value (or values) assigned to the attribute when the user declares it but provides no value.
2. ``required``: a boolean.  If ``True``, the attribute must be declared (and if it is nested, all its antecedent attributes must be declared too).  If ``False``, no defaults are assigned: the user need not declare the attribute at all, but declaring it without providing a value is an error.
3. ``choices``: a list of allowed values; if the user gives a value that is not in the list, an error occurs.  For ``str`` attributes the comparison honors ``case_sensitive`` (below).
4. ``case_sensitive``: for ``str`` attributes only; a boolean that defaults to ``True``.  When ``False``, the user's value is matched against ``choices`` case-insensitively and stored in casefolded (lower-case) form.
5. ``docs``: a block that enriches the output of ``yclept make-doc``.  It may contain ``title`` and ``text`` strings and a YAML-format ``example`` showing the attribute in use.  See :ref:`base_config_docs_key` below.

.. _base_config_docs_key:

Enriching generated documentation with ``docs``
-------------------------------------------------

The ``text`` key gives every attribute a one-line description that appears in
interactive help and generated documentation.  When you want richer, prose
documentation for an attribute — the kind you would write into a reference
manual — add a ``docs`` block.  It is used only by ``yclept make-doc`` and is
ignored during configuration validation:

.. code-block:: yaml

  - name: integrator
    type: str
    text: Integration scheme to use
    choices: [verlet, langevin]
    default: verlet
    docs:
      title: Integration scheme
      text: |
        Selects the time-integration algorithm.  ``verlet`` is symplectic and
        conserves energy well; ``langevin`` couples the system to a heat bath
        and is appropriate for constant-temperature runs.
      example:
        integrator: langevin

``title`` and ``text`` supply a heading and prose for the attribute's generated
page, and ``example`` is rendered as a YAML code block showing the attribute in
use.  See :ref:`usage_yclept_makedoc` for how the tree is generated.
