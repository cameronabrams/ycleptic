# Roadmap

A running list of planned improvements to ycleptic. Items are grouped by theme
and roughly ordered by value within each group. Checked items have shipped;
unchecked items are open. When an item ships, move its summary into
the {doc}`changelog` and check it off here.

## Correctness & validation

- [x] **Complete type validation for non-string scalars.** `dwalk`
  (`ycleptic/walkers.py`) now type-checks user-provided values for
  `int`, `float`, `bool`, and `tuple` attributes, raising `YclepticError` on a
  mismatch. `bool` is kept distinct from the numeric types, an `int` is still
  accepted where a `float` is declared (widening), and a `tuple` attribute
  accepts a YAML sequence — now stored as a tuple rather than discarded.
  *(Shipped.)*
- [x] **Make `make_def` error handling consistent.** The multi-argument branch
  of `make_def` now reports an unrecognized attribute via `raise_clean`, the
  same as the single-argument branch, so every invalid-config error is the
  same catchable `YclepticError`. *(Shipped.)*

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

- [x] **Reconsider the `ycleptic/src/` package layout.** The modules were moved
  up from `ycleptic/src/` to the package root, so internal imports now read as
  `ycleptic.yclept` etc. rather than `ycleptic.src.yclept`. A deprecation shim
  (`ycleptic/src/__init__.py`) keeps the old `ycleptic.src.*` paths working —
  they resolve to the moved modules and emit a `DeprecationWarning`. The
  import-path change warrants a minor version bump at the next release.
  *(Shipped.)*

## Documentation

- [ ] **Document `YclepticError` as public API.** As of 2.1.0, invalid
  configurations raise `ycleptic.YclepticError` instead of terminating the
  interpreter, and the exception is re-exported from the top-level package.
  Add it to the API reference and show the recommended
  `try/except YclepticError` pattern for applications embedding `Yclept`.
  *Effort: low.*
