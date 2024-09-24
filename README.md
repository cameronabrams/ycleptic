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

