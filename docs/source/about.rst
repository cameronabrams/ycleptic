About 
=====

Why Ycleptic?
-------------

I write a lot of Python applications that make use of *input configuration files*.  These are files that users write to describe what specifically they want the application to do for any particular run.  I am sure this is a common element of a lot of programs.  I've written a lot of "user configuration" classes and structures and methods over the years, each one a custom object for the particular program I'm writing.  Ycleptic is my attempt to generalize the configuration class into something that can be easily used for any Python package.

What does Ycleptic do?
----------------------

Ycleptic requires you as a package developer to construct the "base" or "pattern" configuration using a specifically structured YAML file.  Ycleptic parses this base config *and* a user's config to ultimately configure the user's invocation of your package.  What makes this nice from a developer's perspective is that when you want to change *what* is configurable about your package, you only need to edit your app's "base" YAML file.  You can include in that base file restrictions on allowable values for parameters, data types for parameters, whether they are single- or multiple-valued, default values that are filled in automatically when a user omits them, whether a parameter is required, and other things, including documentation.

Even better, the user always has ready access to a help functionality that explains the full configuration syntax, and since your base YAML file should include a text description of any parameter (or set of parameters, or set of set of parameters --- you get the idea), the help is as descriptive as you want it to be.

Ycleptic also supports a personal dotfile or rcfile mechanism: end-users can maintain their own YAML file that extends or overrides selected parts of the base config, which is merged in automatically at load time.

Finally, Ycleptic provides a command-line tool ``yclept make-doc``, that can generate an RST-format documentation tree for your package's configuration.  This is a big deal because it means that you can keep your documentation up to date when you change your base config.  No more "out of date" documentation because you forgot to update it after changing the base configuration file.
