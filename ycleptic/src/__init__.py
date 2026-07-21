# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Deprecated compatibility shim for the old ``ycleptic.src`` layout.

The modules that used to live in ``ycleptic.src`` now live directly under
``ycleptic`` (e.g. ``ycleptic.yclept`` rather than ``ycleptic.src.yclept``).
Importing from ``ycleptic.src`` still works but is deprecated and will be
removed in a future release.
"""

import importlib
import sys
import warnings

warnings.warn(
    "'ycleptic.src' is deprecated; import from 'ycleptic' directly "
    "(e.g. 'ycleptic.yclept' instead of 'ycleptic.src.yclept').",
    DeprecationWarning,
    stacklevel=2,
)

# Alias each moved module under its old ``ycleptic.src.<name>`` path so that
# existing imports keep resolving to the single real module object.
_MOVED = ('yclept', 'walkers', 'dictthings', 'stringthings', 'makedoc', 'errors')
for _name in _MOVED:
    _module = importlib.import_module(f'ycleptic.{_name}')
    sys.modules[f'{__name__}.{_name}'] = _module
    setattr(sys.modules[__name__], _name, _module)
