# Author: Cameron F. Abrams <cfa22@drexel.edu>

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ycleptic")
except PackageNotFoundError:
    __version__ = "unknown"
