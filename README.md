# Ycleptic
> Self-documenting YAML configuration for Python applications

One structured YAML file describes your application's configuration schema. From
that single source of truth, Ycleptic gives you three things that normally live
in three separate places:

1. **Validation & defaults** — a user's YAML config is checked against the
   schema (allowed keys, data types, `choices`, required values), and omitted
   parameters are filled in from their declared defaults.
2. **Generated documentation** — `yclept make-doc` builds an RST/Sphinx
   documentation tree for your config directly from the schema.
3. **Interactive help** — `yclept config-help` lets users explore the
   configuration tree and read the help text for every parameter.

Because the schema is *data* — a YAML file you ship as package data, not a set of
Python classes — editing that one file keeps validation, documentation, and help
in lockstep. No more reference docs drifting out of date because you added a
parameter and forgot to write it up.

## When to use it

Ycleptic fills a specific niche: it shines when your configuration's **schema
should double as its documentation**, and when your users benefit from
*exploring* that configuration interactively — a common situation in scientific
and command-line applications whose users are domain experts rather than
programmers.

It is intentionally **not** a heavyweight validation engine. If your main need is:

- **robust validation, coercion, and rich error messages** — reach for
  [pydantic](https://docs.pydantic.dev/) or
  [jsonschema](https://python-jsonschema.readthedocs.io/);
- **composable, hierarchical config with overrides and interpolation** — reach
  for [Hydra / OmegaConf](https://hydra.cc/).

Ycleptic keeps validation deliberately lightweight and puts its weight behind the
spec-as-documentation workflow. (It also supports a per-user dotfile/rcfile that
extends or overrides the base config, merged in automatically at load time.)

## How it works

As the developer, you write a **base config** that specifies what your users may
configure:

```yaml
# mypackage/data/base.yaml
attributes:
  - name: temperature
    type: float
    text: Simulation temperature in kelvin
    default: 300.0
  - name: integrator
    type: str
    text: Integration scheme to use
    choices: [verlet, langevin]
    default: verlet
```

Your app reads the base config together with the user's config through the
`Yclept` class (typically subclassed):

```python
from ycleptic import Yclept, YclepticError

try:
    config = Yclept(basefile='mypackage/data/base.yaml', userfile=user_yaml)
except YclepticError as e:
    raise SystemExit(f'Invalid configuration: {e}')
```

Then, from the *same* base config, you can generate reference documentation:

```bash
yclept make-doc mypackage/data/base.yaml --root docs/source/config_ref
```

and your users can explore the configuration interactively:

```bash
yclept config-help mypackage/data/base.yaml
```

## Installation

```bash
pip install ycleptic
```

## Documentation

Full documentation is at <https://ycleptic.readthedocs.io/en/latest/>.

## Release History

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See `LICENSE` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

[https://github.com/AbramsGroup](https://github.com/AbramsGroup/)

## Contributing

1. Fork it (<https://github.com/cameronabrams/ycleptic/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
