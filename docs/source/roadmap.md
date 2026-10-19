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

- [x] **No way to express replace-on-present for a list nested inside a bare
  `dict` attribute.** `list_defaults: replace` governs only the `list` attribute
  it is declared on. A list-valued entry inside a `dict` attribute that declares
  no subattributes is merged by `special_update`, which always appends, and
  there is no declaration that changes it — so the schema author cannot say
  "the user's list supersedes mine" at that position at all. This is a step
  worse than the failure class `check-spec` exists for: not a declaration that
  silently does nothing, but a declaration that cannot be written. Raised by
  pestifer 2026-10-16, which has exactly this shape in its relaxation protocols
  and composition sections and expects to hit it.

  Measured 2026-10-19, and the effect is worse than extra entries. The nested
  merge is `special_update`'s, which *deduplicates* but preserves the default's
  ordering, so a user's list is interleaved into the default rather than
  following it: default `steps: [min, nvt, npt]` with the user writing
  `steps: [nvt, custom]` yields `[min, nvt, npt, custom]`. For an ordered
  construct — a relaxation protocol is exactly that — the user's sequence is
  silently rewritten, not merely extended. The two appends in ycleptic are also
  not the same operation: the `list`-attribute path is a plain
  `defaults + I[d]` and does duplicate.

  Fixed by extending `list_defaults` to a `dict` attribute that
  declares no `attributes`, where it governs the list-valued entries of that
  dict's `default`. `append` stays the default at both positions, so no
  existing base config changes behavior. `special_update` gained a `list_mode`
  parameter; `speccheck` now accepts the key there and reports it on a `dict`
  that declares `attributes`; `make-doc` and `console_help` both state the mode
  wherever such a default is shown, which is what the single-source-of-truth
  invariant requires. A list nested deeper than the top level of the default is
  still overwritten by `dict.update` under either mode, documented rather than
  quietly corrected. *(Shipped.)*

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

- [x] **Document `YclepticError` as public API.** Added an "Handling
  configuration errors" section to `usage/class.rst` showing the recommended
  `try/except YclepticError` pattern for embedding applications, rendered the
  exception via `autoexception`, and added an `errors` module page to the API
  reference. *(Shipped.)*
