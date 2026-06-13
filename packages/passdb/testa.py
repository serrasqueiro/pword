# testa.py  (c)2026  Henrique Moreira

""" Testing outputs from mi-files
"""
# pylint: disable=missing-function-docstring

import sys
import passdb

SHOW_SECRETS = True


def main():
    """ Main script
    """
    assert do_script(sys.argv[1:]) is not None, "See testa.py"


def do_script(args):
    param = args
    if not param:
        tup = do_basic_test()
        return tup
    cmd, rest = param[0], param[1:]
    assert not rest, "0 or 1 param!"
    if cmd == "a":
        tup = do_show_referenced()
        return tup
    print("Invalid command:", cmd)
    return None


def do_basic_test():
    """ Basic showing test. """
    poly_test()
    adb = passdb.ADatabase(name="mydata")
    if adb.msg:
        print("ERROR:", adb.msg)
        return 1, adb
    dump_sev(adb, SHOW_SECRETS)
    print("----\n" + "ADatabase().get_basedir():", adb.get_basedir())
    print("CRC32 clashes:", adb.crc_clashes())
    return 0, adb


def dump_sev(adb, show_secret=False):
    """ Dump several stuff. """
    dct = adb.get_tree()["d"]
    pwd_key = adb.get_tree()["c"]
    #print(pwd_key, end=("\n" + "++" * 20 + "\n\n"))
    for key, item in dct.items():
        s_hex = passdb.CRC32.compute_hex(key)
        a_pass = pwd_key[key]
        shown = [key, a_pass] if show_secret else [key]
        print(
            "Tree d:",
            s_hex,
            f"key={key}",
            shown,
            f"Items: {len(item)}, {item}",
        )
    for key, item in adb.get_tree()["f"].items():
        print("CRC:", key, item)


def poly_test():
    """ quoted from
	https://www.researchgate.net/figure/Collision-example-under-CRC-check-The-CRC-checksum-values-of-redundant-and-cyjefpl_fig2_378116852
    """
    astr1, astr2 = "redundant", "cyjefpl"
    hex1 = passdb.CRC32.compute_hex(astr1)
    hex2 = passdb.CRC32.compute_hex(astr2)
    print(hex1, astr1)
    print(hex2, astr2)
    assert hex1 == hex2, "Miss!"
    print("+++" * 8)


def do_show_referenced():
    """ Show referenced passwords, ordered by descendant number of references.
    Only counts when stuff is of relevance.
    """
    adb = passdb.ADatabase(name="mydata")
    dct = adb.get_tree()["d"]
    imp = {}
    for key, seq in dct.items():
        lst = [
            trip for trip in seq
            if interesting(adb, trip[0])
        ]
        if not lst:
            continue
        imp[key] = lst
    sorted_keys = sorted(
        imp.keys(), key=lambda k: len(imp[k]),
        reverse=True,
    )
    for idx, key in enumerate(sorted_keys, 1):
        seq = imp[key]
        print(
            f"idx{idx}/{len(sorted_keys)}:",
            len(seq),
            key, seq,
            end="\n\n",
        )
    #print(adb.get_tree()["g"])
    return 0, adb

def interesting(adb, key, min_val=4):
    ranks = adb.get_tree()["g"]
    tup = ranks.get(key, (min_val, ''))
    return 0 < tup[0] <= min_val


if __name__ == "__main__":
    main()
