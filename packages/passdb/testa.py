# testa.py  (c)2026  Henrique Moreira

""" Testing outputs from mi-files
"""
# pylint: disable=missing-function-docstring

import sys
import passdb


def main():
    """ Main script
    """
    do_script(sys.argv[1:])


def do_script(args):
    param = args
    assert not param, "No params expected."
    adb = passdb.ADatabase(name="mydata")
    msg = adb.full_check()
    if msg:
        print("ERROR:", msg)
        return 1, adb
    dump_sev(adb, True)
    return 0, adb


def dump_sev(adb, show_secret=False):
    """ Dump several stuff. """
    dct = adb.get_tree()["d"]
    pwd_key = adb.get_tree()["c"]["key"]
    #print(pwd_key, end=("\n" + "++" * 20 + "\n\n"))
    for key, item in dct.items():
        s_hex = passdb.CRC32.compute_hex(key)
        a_pass = pwd_key[key]
        shown = [key, a_pass] if show_secret else [key]
        print(
            "Tree d:",
            s_hex,
            shown,
            f"Items: {len(item)}, {item}",
        )


if __name__ == "__main__":
    main()
