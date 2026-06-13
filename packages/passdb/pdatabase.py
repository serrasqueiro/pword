# pdatabase.py  (c)2026  Henrique Moreira

""" mi-files database
"""

# pylint: disable=missing-function-docstring

import os


def main_test():
    adb = ADatabase(name="mydata")
    print("Show container():")
    seq = adb.listed()
    print('\n'.join(seq[0]) + "\n<<< 'accs'", end="\n\n")
    print("upkeys():", adb.upkeys("users"))


class ADatabase:
    """ Any Database with potential 'key_abs_path' configuration file. """
    my_encoding = "ascii"

    def __init__(self, basedir="", config="", name="ADB"):
        self.name = name
        self._basedir, self._okdir = "", False
        self._cont, self._keybase = {}, {}
        self._tree = {}
        self._init_config(
            basedir, config,
            os.path.join(
                os.path.expanduser("~"),
                ".config", "pcheckers", "config",
            )
        )
        self.load(
            ["accs", "users", "info", "pmap", "rank"],
        )

    def get_tree(self):
        """ Returns the tree dictionary. """
        return self._tree

    def container(self, mif=None):
        if mif is None:
            return self._cont
        return self._cont[mif]

    def listed(self, mif=""):
        """ Return the list """
        if mif:
            return list(self._cont[mif][1])
        res = []
        for tbl in sorted(self._cont):
            res.append(self.listed(tbl))
        return res

    def keys(self, mif=None):
        return self._keybase if mif is None else self._keybase[mif]["key"]

    def upkeys(self, mif=None):
        return self._keybase if mif is None else self._keybase[mif]["up-key"]

    def load(self, mi_list):
        for mif in mi_list:
            head, tail = self._load_one(mif)
            self._cont[mif] = (head, tail)
        return sorted(self._cont)

    def full_check(self):
        """ Does the complete consistency check,
        returns empty string if all ok!
        """
        msg = self._check_1()
        if msg:
            return msg
        msg = self._check_2()
        return msg

    def _load_one(self, mif):
        """ Load one mi-file. """
        assert len(mif) >= 4, mif
        path = os.path.join(self._basedir, mif) + ".mi"
        with open(path, "r", encoding=ADatabase.my_encoding) as fdin:
            lst = fdin.readlines()
        self._keybase[mif] = {
            "key": {},
            "up-key": {},
        }
        head, tail = lst[0].rstrip(), self._strict_list(lst[1:], mif)
        return head, tail

    def _strict_list(self, lst, mif, stt_idx=2):
        assert mif, self.name
        for idx, line in enumerate(lst, stt_idx):
            assert line.endswith("\n"), f"Bad line ({mif}): {idx}"
            astr = line[:-1]
            # e.g. ACCOR;hclm;p
            keypair = astr.split(";", maxsplit=1)
            key, rvalue = keypair
            assert key, self.name
            upkey = ''.join([achr.upper() for achr in key if achr > ' '])
            assert key not in self._keybase[mif]["key"], f"Already there ({mif}): {idx}: {key}"
            self._keybase[mif]["key"][key] = rvalue
            assert upkey not in self._keybase[mif]["up-key"], f"Already there, up-key ({mif}): {idx}: {upkey}"
            self._keybase[mif]["up-key"][upkey] = rvalue
            yield astr

    def _check_1(self):
        """ First level checking:
		1. An account username is known.
        """
        if not self._tree:
            self._tree = self._get_tree(self._keybase)
        return ""

    def _check_2(self):
        """ Second level checking:
		* Check all password references are valid.
        """
        # Check if any pass is orphan (unused)
        for key, item in self._tree["d"].items():
            if not item:
                msg = f"Unused pass ref: {[key]}"
                return msg
        return ""

    def _init_config(self, basedir, config, def_config):
        if config:
            cfg_path = config
        else:
            cfg_path = def_config
        cfg = load_simple_config(
            basedir if basedir else cfg_path
        )
        key_abs_path = os.path.realpath(cfg["key_abs_path"])
        is_ok = os.path.isdir(key_abs_path)
        self._basedir, self._base = key_abs_path, is_ok
        return True

    def _get_tree(self, dct):
        """ Get entire database tree.
        """
        tree = {
            "a": {},	# Accounts
            "b": {},	# B-users
            "c": {},	# Convert passwords
            "d": {},	# D-used pass reference by user
        }
        pwds = {}
        accs, users = dct["accs"], dct["users"]
        assert not accs["key"], "Unexpected iterator (yield)"
        self.listed()
        for key, item in accs["key"].items():
            user, p_ref = item.split(";", maxsplit=1)
            tree["a"][key] = (user, p_ref)
            if p_ref in pwds:
                pwds[p_ref].append(user)
            else:
                pwds[p_ref] = [user]
        for key, item in users["key"].items():
            assert item, f"Missing user referenced as: {[key]}"
            tree["b"][key] = item
        for key, item in dct["pmap"].items():
            tree["c"][key] = item
        tree["d"] = pwds
        return tree


def load_simple_config(path, enc_in="ascii"):
    cfg = {}
    with open(path, "r", encoding=enc_in) as fdin:
        lines = fdin.readlines()
    for idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", maxsplit=1)
            cfg[key.strip()] = value.strip()
        else:
            cfg[line] = idx
    return cfg


if __name__ == "__main__":
    main_test()
