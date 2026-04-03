# pword

Main class is `MiLot`, is not a password checker in the sense of verifying user input.
Instead, it is a database loader and validator that:
- Reads .mi files
- Ensures internal consistency
- Exposes a method to retrieve credentials

It is essentially a mini-database engine for text-based credential storage.

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
1. `is_ok = mis.process_path(pconf.main_path(), debug=0) == 0`
1. `assert is_ok and mis.dump_db() == True, "All OK!"`
1. `accs, usrs, pmap, rank = mis.dbm["accs"], mis.dbm["users"], mis.dbm["pmap"], mis.dbm["rank"]`
