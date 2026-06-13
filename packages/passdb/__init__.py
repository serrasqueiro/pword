""" passdb -- Password database dumper/ checker

bpython debug:
```python
import importlib, passdb; importlib.reload(passdb)
```

"""

COMPAT_PWORD_VERSION = "1.22 16"

VERSION = "1.30 21"

from .pdatabase import ADatabase
from .poly import CRC32, crc32_hex

__all__ = [
    "ADatabase",
    "CRC32",
    # "crc32_hex"  <-- prefer CRC32
]
