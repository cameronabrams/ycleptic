# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Exception types raised by ycleptic
"""

from __future__ import annotations


class YclepticError(Exception):
    """
    Raised when a user configuration is invalid.

    Library code raises this exception instead of terminating the interpreter,
    so applications embedding :class:`~ycleptic.yclept.Yclept` can catch it
    and handle invalid configurations gracefully.  The command-line interface
    catches :class:`YclepticError` and reports it as a clean, traceback-free
    error message.
    """
