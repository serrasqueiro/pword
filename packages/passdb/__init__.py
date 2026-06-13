""" passdb -- Password database dumper/ checker

bpython debug:
```python
import importlib, passdb; importlib.reload(passdb)
```
"""

from .pdatabase import ADatabase
from .phashing import PHasher
from .poly import CRC32


COMPAT_PWORD_VERSION = "1.22 16"

VERSION = "1.30 21"

__all__ = [
    "ADatabase",
    "CRC32",
    "PHasher",
]
