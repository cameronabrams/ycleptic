# Roadmap

A running list of planned improvements to ycleptic. Items are grouped by theme
and roughly ordered by value within each group. Checked items have shipped;
unchecked items are open. When an item ships, move its summary into
the {doc}`changelog` and check it off here.

## Correctness & validation

- [ ] **Complete type validation for non-string scalars.** `dwalk`
  (`ycleptic/src/walkers.py`) only validates `str` values (and only their
  `choices`). Attributes declared `type: int`, `float`, `bool`, or `tuple`
  accept user values of the wrong type without complaint, so the datatype
  guarantee the README advertises is only partially enforced. Add explicit
  type checks (raising `YclepticError`) for the remaining scalar types.
  *Effort: medium.*
- [ ] **Make `make_def` error handling consistent.** In
  `ycleptic/src/walkers.py`, the single-argument branch of `make_def` reports
  an unrecognized attribute via `raise_clean` (now `YclepticError`), while the
  multi-argument branch still does a bare `raise ValueError`. Route both
  through `raise_clean` so every invalid-config error is the same catchable
  type. *Effort: trivial (one line).*

## Tooling & CI

- [x] **Run the test suite in CI on every push/PR.** Added
  `.github/workflows/ci.yaml` with a `test` job that runs `pytest` across
  Python 3.9–3.13 on every push to `main` and every pull request. *(Shipped.)*
- [x] **Add lint and type-check configuration.** Configured `ruff` (lint with
  flake8-bugbear, plus single-quote formatting) and a lenient `mypy` pass in
  `pyproject.toml`, added a `lint` optional-dependency group, and wired a
  `lint` job (`ruff check`, `ruff format --check`, `mypy`) into
  `ci.yaml`. Bugbear caught the mutable default `docexample: dict = {}` in
  `make_doc` and the implicit-`Optional` defaults, which are now fixed.
  *(Shipped.)*

## Structure & public API

- [ ] **Reconsider the `ycleptic/src/` package layout.** The importable package
  contains a `src` subpackage, so internal imports read as
  `ycleptic.src.yclept`. This inverts the usual meaning of a `src`-*layout*
  (`src/ycleptic/…`) and leaks `src` into import paths. Flattening to
  `ycleptic/yclept.py` etc. would be cleaner, but it is a breaking change for
  anyone importing internals, so it needs a deprecation shim and a minor/major
  version bump. *Effort: medium; coordinate with a version bump.*

## Documentation

- [ ] **Document `YclepticError` as public API.** As of 2.1.0, invalid
  configurations raise `ycleptic.YclepticError` instead of terminating the
  interpreter, and the exception is re-exported from the top-level package.
  Add it to the API reference and show the recommended
  `try/except YclepticError` pattern for applications embedding `Yclept`.
  *Effort: low.*
