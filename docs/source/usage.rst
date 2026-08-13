Usage
=====

``Ycleptic`` primarily exposes the :class:`ycleptic.yclept.Yclept` class to inherit in your own applications.  It also has a command-line interface with three subcommands: ``yclept config-help`` provides interactive help for the configuration file, ``yclept make-doc`` generates documentation from the base configuration file, and ``yclept check-spec`` reports declarations in a base configuration file that ycleptic ignores.

.. toctree::
   :maxdepth: 1

   usage/quickstart
   usage/class
   usage/the_base_config
   usage/the_user_config
   usage/interactive_help
   usage/resource_file
   usage/yclept_config-help
   usage/yclept_makedoc
   usage/yclept_check-spec