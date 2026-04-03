# pword

## Quick User Guide
In order to dump database, use:
- `pcheckers.py`, the following command:
  * `pcheckers.py -c abc` will dump information about accounts starting by _abc_
In order to do a quick dump, showing the abstract accounts and simple passwords:
- `pchreader.py`, the following command:
  * `pchreader.py ~/mi_files/` will dump that database comprehensively.
To dump current (private) configuration, do:
- `pcheckersconfig.py`

## Developers Quick How To

1. `import importlib; import pword; importlib.reload(pword)`
   + use just `import pword` if needed
1. `pconf = pword.pcheckersconfig.PConfig()`
1. `mis = MiLot(alt_tables=True)`
1. `mis.process_path(pconf.main_path(), debug=1)`
1. `assert mis.dump_db() == True, "All OK!"`
