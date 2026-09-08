# CLAUDE.md — working notes for ycleptic

Ycleptic turns one YAML file — the **base config**, a schema written as *data* —
into three things at once: validation of a user's config, a generated Sphinx
doctree, and an interactive help browser. The whole point is that those three
never drift apart, because they all read the same file. Keep that invariant in
mind before adding a feature: **anything that teaches the validator a new trick
must also teach `make-doc` and `console_help` the same trick**, or the schema
stops being a single source of truth. The v2.3.0 `choices` fix was exactly this
bug — interactive help showed allowed values, generated docs did not.

## Layout

    ycleptic/
      yclept.py       Yclept(UserDict) — the public class; loads base + user,
                      make_doctree(), console_help(), dump_user(),
                      make_default_specs()
      walkers.py      the recursive core: dwalk (validate/fill a dict level),
                      lwalk (a list of task-items), mwalk (merge an rc/dotfile
                      base into the app base), make_def (defaults for a subtree)
      speccheck.py    validates the base config *itself* — the recognized-key
                      and recognized-type vocabulary lives here
      makedoc.py      base spec -> RST tree
      cli.py          `yclept` entry point: make-doc, config-help, check-spec
      errors.py       YclepticError, YclepticSpecWarning
      dictthings.py   special_update (list-append / dict-merge semantics)
      stringthings.py raise_clean, oxford, footer + RST helpers
      resources/example_base.yaml   the shipped example schema
      src/__init__.py deprecation shim for the pre-2.3 `ycleptic.src.*` paths

`docs/source/` mirrors this: `usage/` is hand-written prose, `api/` is autodoc
stubs — a new module needs a new `api/ycleptic.<mod>.rst`.

## Two kinds of validation — don't confuse them

1. **User config vs. base config** — `dwalk`/`lwalk`. Failures are the user's
   fault. They raise `YclepticError` via `raise_clean()`.
2. **Base config vs. ycleptic's own vocabulary** — `speccheck.check_base_spec`.
   Failures are the *schema author's* fault: a key or type name ycleptic does
   not read, which is therefore silently discarded. These warn
   (`YclepticSpecWarning`) so existing schemas keep loading;
   `Yclept(..., strict_spec=True)` promotes them to errors, and
   `yclept check-spec` exits nonzero so CI can gate on them.

Because a base config is data, **an unrecognized key is not an error, it is a
no-op** — that is the failure mode speccheck exists to surface. If you add a
key or type name to the schema vocabulary, add it to `KNOWN_ATTRIBUTE_KEYS`,
`KNOWN_DOCS_KEYS`, `KNOWN_TOP_KEYS`, or `KNOWN_TYPES` in `speccheck.py` in the
same change, or `check-spec` will start reporting your own new feature as a
mistake. Consider adding a `_KEY_ALIASES`/`_TYPE_ALIASES` entry for the
misspelling people will actually make; anything else falls back to difflib.

## Error convention

Library code never calls `sys.exit`. It calls
`raise_clean(ValueError(...))`, which re-raises the message as a
`YclepticError` with `from None` so embedding applications get a clean,
catchable exception and the CLI gets a traceback-free message. New validation
failures should follow this — a bare `raise ValueError` leaks a traceback and
is not part of the documented `try/except YclepticError` contract.

## Typing rules that look like bugs but are deliberate

In `walkers._scalar_type_ok`:

- `bool` is **not** an `int`. A YAML boolean must not satisfy a numeric
  attribute, so both the `int` and `float` checks explicitly exclude `bool`.
- an `int` **is** accepted where `float` is declared (widening).
- a YAML sequence satisfies `tuple` — YAML has no tuple type — and is stored
  as a real `tuple`.
- `str` is not type-checked here at all; string attributes are constrained
  through `choices` (and `case_sensitive`, which casefolds in place).
- `choices` is only enforced on `str`. Declaring it elsewhere does nothing,
  which is why speccheck reports it.

Defaults merge, they do not overwrite: a `dict` attribute with no
subattributes merges the user's value into the default via `special_update`
(lists append, dicts merge, scalars overwrite); a `list` attribute prepends its
default (`defaults + I[d]`). Changing this quietly changes behavior for every
downstream app.

## Conventions

- `I` is the input/user dict parameter throughout `walkers.py`; ruff's `E741`
  is disabled repo-wide for exactly this reason. Don't rename it piecemeal.
- Single quotes — `ruff format` is configured with `quote-style = 'single'`,
  and CI runs `ruff format --check`.
- Public re-exports in `ycleptic/__init__.py` must follow the `__version__`
  assignment, so `E402` is ignored there.
- `__version__` comes from installed package metadata, not a literal; only
  `pyproject.toml` carries the version, and only `release.sh` edits it.

**A consequence of that last point, which has bitten a downstream consumer.**
Between releases, `main` carries the *previous* release's version number —
unreleased work on `main` today still reports `2.3.0`. The code is current; only
the number lags. Anything that keys on the version rather than the tree cannot
tell the difference: `uv` and `pip` wheel caches will happily serve a cached
`2.3.0` artifact built from older source. Symptoms are new features appearing
absent while the checkout plainly contains them.

When testing a consumer against an unreleased checkout, verify what you actually
loaded rather than trusting the version:

    python -c "import ycleptic, ycleptic.walkers as w; \
               print(ycleptic.__file__, hasattr(w, 'subattributes'))"

An editable install, `PYTHONPATH`, or `uv run --project <checkout>` all resolve
to the working tree; a plain non-editable install of the checkout is the case
that can be served stale.

`uv run --with <checkout>` is the trap, and it is silent. If the consuming
project declares `ycleptic>=2.3.0` and the checkout also calls itself `2.3.0`,
the floor is already satisfied and uv may resolve to the PyPI build instead of
the path you named. Nothing errors, and the version string is identical either
way, so the only reliable gate is file content — check `ycleptic.__file__`, or
probe for a symbol the branch introduced. Observed 2026-09-08 while a downstream
repo tried to test against an unreleased branch.

## Working commands

    uv run --extra test pytest tests -q      # 52 tests, <1s. NOT tests/unit
    uv run --extra lint ruff check ycleptic/
    uv run --extra lint ruff format --check ycleptic/
    uv run --extra lint mypy ycleptic/

Tests live in one file, `tests/test_set.py` (single `TestYclept` unittest
class). `tests/conftest.py` chdirs each test into `tests/test_set/`, so tests
read and write fixture files by bare filename; several test outputs there are
gitignored. `tests/test_set/test_package/` is a miniature installable package
used to exercise `make-doc` against a realistic app layout.

CI (`.github/workflows/ci.yaml`) runs pytest on Python 3.9–3.13 plus a lint job.
The floor is **3.9**, so no `match`, no PEP 604 unions at runtime — every module that
needs a modern annotation carries `from __future__ import annotations` and
relies on it.

## Releasing

    scripts/release.sh <version>

It rotates `CHANGELOG.md`'s `[Unreleased]` section, bumps `pyproject.toml`,
commits, tags, and pushes. **Pushing the tag is what publishes to PyPI.** Never
hand-roll any of those steps. Write the changelog entries under `[Unreleased]`
as you go, not at release time.

`pestifer` pins `ycleptic>=2.3.0` and is the only known downstream consumer —
coordinate with it before a release that moves the floor, and keep the
`ycleptic.src` deprecation shim until it is confirmed unused.
