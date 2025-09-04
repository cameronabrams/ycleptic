# Ycleptic
> YAML configuration generator

YAML is a popular markup language for input files, with its easy syntax and clear
mapping to lists and dicts.  Ycleptic allows a developer to specify all keys, datatypes,
default values, choice restrictions, and other features of YAML-format input 
files for use in their own apps. This makes the specification of input file syntax on top 
of YAML for any particular application a bit easier than just using pure YAML.  In addition,
ycleptic can also automatically build the RST/Sphinx doctree for your app's configuration
file.

## Installation

```bash
pip install ycleptic
```

Once installed, the developer has access to the ``Yclept`` class.

## Release History
* 2.0.3
    * refactored to change `directive` to `attribute` throughout
* 1.9.0
    * new `update_user` method
* 1.8.1
    * fixed faulty special update of dict-like values with defaults
* 1.8.0
    * more informative error messages via `raise_clean`
* 1.7.0
    * Restructured code-base and expanded documentation
* 1.6.2
    * `footer-style` argument added to `make-docs`
* 1.5.0
    * `example` subfield in `docs` directive enabled
* 1.4.1
    * `case_sensitive` boolean attribute enabled for all `str`-types
* 1.3.0
    * `__init__` optionally accepts a dict instead of only a file name
* 1.2.0
    * `make-doc` subcommand upgraded to put RST links at the top of every RST file
* 1.1.0
    * bugfix: shows default values for any dict-type parameters
    * bugfix: `choices` in interactive help did not work with integer choices
* 1.0.7
    * bugfix: bad string in doc builder
* 1.0.6
    * interactive mode implemented
    * `config-help` subcommand added
    * `make-doc` subcommand added
* 1.0.5
    * added support for a user dotfile/rcfile
* 1.0.4
    * added `**kwargs` to `console_help` to allow override of `print`
* 1.0.3.3
    * fixed spurious output
* 1.0.3.2
    * fixed version detection bug
* 1.0.2
    * Updated documentation; added version detection
* 1.0.1
    * Include example base config
* 1.0.0
    * Initial version

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

[https://github.com/AbramsGroup](https://github.com/AbramsGroup/)

## Contributing

1. Fork it (<https://github.com/AbramsGroup/HTPolyNet/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

