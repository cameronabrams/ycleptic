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


class YclepticSpecWarning(UserWarning):
    """
    Issued when a base config specification contains a declaration ycleptic
    ignores, such as a misspelled key or an unrecognized type name.

    Such a declaration does nothing, so an attribute its author believes is
    constrained may in fact accept any value.  This is a warning rather than an
    error so that existing specifications keep loading; construct
    :class:`~ycleptic.yclept.Yclept` with ``strict_spec=True`` to raise
    :class:`YclepticError` instead.
    """
