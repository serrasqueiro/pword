""" pword -- Passwords storing

bpython debug:
```python
import importlib, pword; importlib.reload(pword)
```

"""

PWORD_VERSION = "1.22 16"

from .pcheckersconfig import PConfig
from .milot import MiLot, mprint
from .dictilar import DictShown

__all__ = [
    "PConfig",
    "MiLot",
    "mprint",
    "DictShown",
]
