.. _usage_yclept_config_help:

``yclept config-help``
========================

The command-line tool ``yclept config-help <base.yaml>`` lets you use the interactive help feature detailed in :ref:`usage_interactive_help` to explore a base configuration file directly, without writing any code.  For example, if you have a base configuration file called ``base.yaml``, you can run:

.. code-block:: console

   $ yclept config-help base.yaml

which drops you into the interactive explorer:

.. code-block:: console

   $ yclept config-help base.yaml
       attribute_1 ->
       attribute_2 ->
       attribute_3 ->
       .. up
       ! quit
   help: attribute_2

   attribute_2:
       Attribute 2 is interpretable as an ordered list of attributes

   base|attribute_2
       attribute_2a ->
       attribute_2b ->
       .. up
       ! quit
   help: !

At each prompt, type an attribute name to drill into it, ``..`` to go back up a
level, and ``!`` to quit.  A trailing ``->`` marks an attribute that has
subattributes.  You can also pass a space-separated attribute path on the
command line to jump straight to a node, for example:

.. code-block:: console

   $ yclept config-help base.yaml attribute_2 attribute_2a
