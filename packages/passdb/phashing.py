# phashing.py  (c)2026  Henrique Moreira

""" mi-files autonomous (CRC32) hashing
"""

# pylint: disable=missing-function-docstring

import os


class PHasher:
    """ Password hasher. """
    pcrc_name = "pcrc.mi"

    def __init__(self, adb):
        self._adb = adb
        self.a_keys, self.sort_keys = [], []
        self.imp = []

    def get_db(self):
        return self._adb

    def builder(self):
        adb = self._adb
        dct = adb.get_tree()["d"]
        users = adb.get_tree()["b"]
        imp = {}
        assert adb.crc_clashes() == 0, "Don't know how to handle clashes at pass references."
        for key, seq in dct.items():
            lst = [
                (trip[0], users[trip[1]]) for trip in seq
                if interesting(adb, trip[0])
            ]
            if not lst:
                continue
            imp[key] = (
                seq[0][2] + ".1",
                lst,
            )
        sorted_keys = sorted(
            imp.keys(), key=lambda k: len(imp[k][1]),
            reverse=True,
        )
        self.a_keys = sorted(adb.get_tree()["a"])
        self.sort_keys = sorted_keys
        self.imp = imp
        return imp

    def dump_important(self, sep="\n\n"):
        keys = self.sort_keys
        for idx, key in enumerate(keys, 1):
            crc, seq = self.imp[key]
            print(
                f"idx{idx}/{len(keys)}:",
                crc,
                len(seq),
                key, seq,
                end=sep,
            )
        #print(adb.get_tree()["g"])

    def brute_save(self):
        bdir = self._adb.get_basedir()
        if not bdir or not self.sort_keys:
            return False
        fname = os.path.join(
            bdir,
            PHasher.pcrc_name,
        )
        astr = "#crc32.1;p_ref\n"
        for key in self.sort_keys:
            crc, seq = self.imp[key]
            line = f"{crc};{key}"
            astr += line + "\n"
        with open(fname, "w", encoding="ascii") as fdout:
            fdout.write(astr)
        return True


def interesting(adb, key, min_val=4):
    ranks = adb.get_tree()["g"]
    tup = ranks.get(key, (min_val, ''))
    return 0 < tup[0] <= min_val
