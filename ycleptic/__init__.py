# Author: Cameron F. Abrams <cfa22@drexel.edu>

import logging
from importlib.metadata import version, PackageNotFoundError

__version__: str
try:
    __version__ = version('ycleptic')
except PackageNotFoundError:
    __version__ = 'unknown'

logging.getLogger(__name__).addHandler(logging.NullHandler())

from ycleptic.src.yclept import Yclept
from ycleptic.src.errors import YclepticError

__all__ = ['Yclept', 'YclepticError']
