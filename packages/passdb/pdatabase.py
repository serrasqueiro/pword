# pdatabase.py  (c)2026  Henrique Moreira

""" mi-files database
"""

# pylint: disable=missing-function-docstring

import os
from .poly import CRC32


def main_test():
    adb = ADatabase(name="mydata")
    print("Show container():")
    seq = adb.listed()
    print('\n'.join(seq[0]) + "\n<<< 'accs'", end="\n\n")
    print("upkeys():", adb.upkeys("users"))


class ADatabase:
    """ Any Database with potential 'key_abs_path' configuration file. """
    my_encoding = "ascii"

    def __init__(self, basedir="", config="", check=True, name="ADB"):
        self.name = name
        self.msg = ""
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
        if check:
            self._do_all_checks()

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

    def crc_clashes(self):
        dct = self._tree["j"]
        lst = [
            dct[clash] for clash in dct if clash > 1
        ]
        return sum(lst)

    def full_check(self):
        """ Does the complete consistency check,
        returns empty string if all ok!
        """
        msg = self._check_1()
        if msg:
            return msg
        msg = self._check_2()
        if msg:
            return msg
        msg = self._check_3()
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
        return head,tail

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

    def _do_all_checks(self):
        self.msg = self.full_check()
        return self.msg

    def _check_1(self):
        """ First level checking:
		1. An account username is known.
		2. An account password exists.
        """
        if not self._tree:
            self._tree = self._build_tree(self._keybase)
        users = self._tree["b"]
        for key, item in self._tree["a"].items():
            user_ref = users.get(item[0])
            if user_ref is None:
                return f"Account (key={[key]}) references missing user: {item[0]}"
            a_pass = self._tree["c"].get(item[1])
            if a_pass is None:
                return f"Account (key={[key]}) references inexisting pass reference: {item[1]}"
        return ""

    def _check_2(self):
        """ Second level checking:
		1. Check all users are referenced by accounts.
        """
        accs, users = self._tree["a"], self._tree["b"]
        used = {key: 0 for key in users}
        for key, item in accs.items():
            user = item[0]
            used[user] += 1
        res = []
        for user in sorted(used):
            if used[user] <= 0:
                res.append(user)
        if len(res) == 1:
            return f"One orphan user: {res}"
        if len(res) >= 4:
            return "More than one orphan user: {} (...)".format(
                ', '.join(res[:4]),
            )
        elif res:
            return f"Several orphan users: {res}"
        return ""

    def _check_3(self):
        """ Check ranks match any of accounts.
        Also check users at info.mi exist!
        """
        for key, item in self._tree["g"].items():
            wot = self._tree["a"].get(key)
            if wot is None:
                return f"Rank with invalid account id: {[key]}"
        for key, item in self._tree["i"].items():
            if key not in self._tree["a"]:
                return f"Info with invalid account id: {[key]}"
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

    def _build_tree(self, dct):
        """ Get entire database tree.
        """
        tree = {
            "a": {},	# Accounts
            "b": {},	# B-users
            "c": {},	# Convert passwords
            "d": {},	# D-used pass reference by user
            "e": {},	# CRC32 'F0491F19': ['7119']
            "f": {},	# same as 'e' but with CRC32.1 if there is only one
            "g": {},	# Ranks
            "i": {},	# Info
            "j": {
                1:0, 2:0, 3:0,	# Only up to 3 clashes in CRC32 allowed
            }
        }
        pwds = {}
        accs, users = dct["accs"], dct["users"]
        assert not accs["key"], "Unexpected iterator (yield)"
        self.listed()
        for key, item in accs["key"].items():
            user, p_ref = item.split(";", maxsplit=1)
            tree["a"][key] = (user, p_ref)
            h_crc = hex_crc(p_ref)
            stg = (key, user, h_crc)
            if p_ref in pwds:
                pwds[p_ref].append(stg)
            else:
                pwds[p_ref] = [stg]
            if h_crc in tree["e"]:
                tree["e"][h_crc] = list(set(tree["e"][h_crc] + [p_ref]))
            else:
                tree["e"][h_crc] = [p_ref]
        for key, item in users["key"].items():
            assert item, f"Missing user referenced as: {[key]}"
            tree["b"][key] = item
        for key, item in dct["pmap"]["key"].items():
            assert key not in tree["c"], f"Duplicate pmap: {key}"
            tree["c"][key] = item
        tree["d"] = pwds
        for key, item in tree["e"].items():
            n_clash = len(item)
            tree["j"][n_clash] += 1
            tree["f"][f"{key}.{n_clash}"] = tuple(item)
        for key, item in dct["rank"]["key"].items():
            tup = item.split(";", maxsplit=1)
            aval, opt_extra = tup
            assert 0 <= int(aval) <= 9, f"Invalid rank number for {[key]}: {aval}"
            tree["g"][key] = (int(aval), opt_extra)
        for key, item in dct["info"]["key"].items():
            tree["i"][key] = item
        return tree


def hex_crc(astr: str):
    """ Returns CRC32 8-char (4 nibbles) string """
    assert isinstance(astr, str), "hex()"
    hstr = CRC32.compute_hex(astr)
    return hstr


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
