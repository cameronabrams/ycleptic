# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- restructured package

## [2.0.4] - 2026-05-01

### Fixed
- RTD workflow was triggering docs builds on wrong project (`pidibble` instead of `ycleptic`)
- README Contributing section linked to a different repository's fork page
- `test_makedoc` expected string was stale (`"Single-valued parameters:"` → `"Single-valued attributes:"`)
- Bare `except:` clauses in `walkers.py` narrowed to `except ValueError:`
- Mutable default arguments `userdict={}` and `new_data={}` in `Yclept` replaced with `None`-defaulted parameters
- `exit(0)` in `_endhelp` replaced with `sys.exit(0)`
- `D["name"]` in `walkers.dwalk` raised `KeyError` at the root config level; replaced with `D.get("name", "root")`
- `type(x) == list/dict` identity comparisons replaced with `isinstance()` throughout

### Changed
- `make-doc` subcommand and `make_doctree` now accept a path for `--root` (e.g. `docs/source/config_ref`), so the command can be run from the project root without a prior `cd docs/source`; `makedoc.py` refactored from `os.chdir()` traversal to `pathlib.Path` throughout
- Debug `print()` calls in `makedoc.py` and `conf.py` converted to `logging.debug()` and removed respectively
- `docs/requirements.txt` de-duplicated and dead dependencies (`recommonmark`, `commonmark`, `alabaster`, `sphinx-rtd-theme`, `pillow`, `mock`) removed
- `cli.py` `config_help` now has a safe fallback for `write_func` when an unrecognized value is passed

### Added
- `from __future__ import annotations` added to all source modules for Python 3.7/3.8 annotation compatibility
- `logging.NullHandler()` registered in package `__init__` per library logging best practices
- `pytest` step added to release workflow before PyPI publish
- Test suite expanded from 9 to 29 tests; `tearDown` added for automatic cleanup of generated files
- Test-generated output files added to `.gitignore`
- This changelog

---

## [2.0.3] - 2025-09-04

- Renamed `directive` to `attribute` throughout codebase and documentation

## [2.0.2] - 2025-09-04

- Refactored `make_doc` internal path-handling logic

## [2.0.1] - 2025-08-22

- Documentation updates

## [1.9.0] - 2025-08-18

- Added `update_user` method to `Yclept`

## [1.8.1] - 2025-08-04

- Fixed faulty special update of dict-like values with defaults

## [1.8.0] - 2025-07-29

- More informative error messages via `raise_clean`

## [1.7.0] - 2025-07-16

- Restructured code-base and expanded documentation

## [1.6.2] - 2025-06-18

- Added `--footer-style` argument to `make-doc` CLI command

## [1.6.1] - 2025-06-18

- Version and configuration housekeeping

## [1.6.0] - 2025-06-18

- Internal release

## [1.5.0] - 2025-06-15

- Added `example` subfield to `docs` attribute specification

## [1.4.1] - 2025-05-21

- Enabled `case_sensitive` boolean for all `str`-type attributes

## [1.4.0] - 2025-05-21

- Initial implementation of `case_sensitive` attribute

## [1.3.0] - 2025-04-01

- `Yclept.__init__` now accepts a `userdict` dict in addition to a file path

## [1.2.0] - 2025-02-10

- `make-doc` subcommand now emits RST cross-reference links at the top of every generated RST file

## [1.1.0]

- Fixed: default values now shown for dict-type attributes in `console_help`
- Fixed: `choices` validation now works with integer choices

## [1.0.7]

- Fixed bad string in doc builder

## [1.0.6]

- Implemented interactive help mode
- Added `config-help` CLI subcommand
- Added `make-doc` CLI subcommand

## [1.0.5]

- Added support for a user dotfile/rcfile

## [1.0.4]

- Added `**kwargs` to `console_help` to allow `write_func` override

## [1.0.3.3]

- Fixed spurious output

## [1.0.3.2]

- Fixed version detection bug

## [1.0.2]

- Updated documentation; added version detection

## [1.0.1]

- Added example base config resource

## [1.0.0]

- Initial release
