ycleptic
========

**Ycleptic** (ee-KLEP-tic) turns a single, structured YAML file into a self-documenting configuration system for your Python application.  From one schema file you get three things at once: validation of a user's config (with defaults, allowed value ``choices``, and required parameters), an automatically generated RST/Sphinx documentation tree, and an interactive help explorer for your users.  Because the schema is data rather than Python code, editing that one file keeps validation, documentation, and help in lockstep.

Ycleptic is intentionally lightweight on validation and focuses on the *spec-as-documentation* workflow — a good fit for scientific and command-line applications whose users are domain experts.  If you need heavyweight validation and coercion, `pydantic <https://docs.pydantic.dev/>`_ or `jsonschema <https://python-jsonschema.readthedocs.io/>`_ are better suited; for composable, hierarchical config, see `Hydra <https://hydra.cc/>`_.

.. note::

   Ycleptic is under active development.

.. note:: 

   Ycleptic is used in the `pestifer <https://pypi.org/project/pestifer/>`_ package.

Contents
--------

.. toctree::
   :maxdepth: 1

   about
   installation
   usage
   API <api/API>
   roadmap
   changelog

