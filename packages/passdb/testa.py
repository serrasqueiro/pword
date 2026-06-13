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
    do_script(sys.argv[1:])


def do_script(args):
    param = args
    assert not param, "No params expected."
    poly_test()
    adb = passdb.ADatabase(name="mydata")
    if adb.msg:
        print("ERROR:", adb.msg)
        return 1, adb
    dump_sev(adb, SHOW_SECRETS)
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


if __name__ == "__main__":
    main()
