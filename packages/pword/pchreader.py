#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2022  Henrique Moreira
""" mi-files dump only
MiLot here is optional. Raw text dump is also used.

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring, consider-using-with

import sys
import os.path
from pword.milot import MiLot

TUP_EXCLUDE = (
    "wix",
)

PASS_EXPOSE_TUPS = (
    "gm-",
)


def main():
    """ Main (non-interactive) script """
    code = process(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

python {__file__} [options] path

Options are:
  -v                Verbose (twice: -v -v, more verbose)

Verbose:
	0	Only dump account pass
	1	Dump basic information (not passes)
	2	Dump complete pass
""")
    sys.exit(code if code else 0)


def process(out, err, args):
    opts = {
        "verbose": 0,
    }
    param = args
    while param and param[0].startswith("-"):
        this = param[0]
        if this.startswith("-v"):
            assert len(this) == this.count("v") + 1, this
            opts["verbose"] += this.count("v")
            del param[0]
            continue
        return None
    if not param:
        return None
    apath = param[0]
    del param[0]
    if param:
        return None
    if opts["verbose"] > 3:
        print("Too much verbose!", end="\n\n")
        return None
    code = do_it(out, err, apath, opts)
    return code


def do_it(out, err, path, opts) -> int:
    """ Main script
    """
    assert path
    verbose = opts["verbose"]
    debug = int(verbose >= 2)
    # Check whether path makes sense
    acc_file = os.path.join(path, "accs.mi")
    accs = acc_reader(acc_file, path)
    # MiLot class instance:
    code, mis = process_milot(err, path, verbose, debug)
    if code:
        return code
    if verbose <= 0:
        simple_dump(out, accs, mis)
        #print("### simple_dump() end:", len(accs), "; last:", accs[-1])
    return 0

def process_milot(err, path, verbose, debug=0) -> tuple:
    """ Open and dump MiLot textual database """
    dump_pass = debug
    mis = MiLot(alt_tables=True)
    code = mis.process_path(path, debug=debug)
    if code:
        err.write(f"Check mi-files failed: error-code {code}\n")
        if mis.dbm:
            print(f"Keys read: {mis.dbm.keys()}")
        return 1, mis
    #shown = [(f"keyval[{idx}]", item) for idx, item in enumerate(mis.dbm["rank"].keyval)]
    shown = mis.dbm["rank"].key_dict()
    if verbose > 0:
        if mis.dbm:
            print(f"# Dumping dbm (debug={debug})")
            mis.dump_db(dump_pass, debug=debug)
    if verbose >= 2:
        for item in sorted(shown):
            print(f"## Rank: '{item}', {shown[item]}")
    return 0, mis

def acc_reader(acc_file, path="") -> list:
    """ Reads textual account file """
    def read_acc(fname):
        with open(fname, "r", encoding="ascii") as fdin:
            res = fdin.readlines()
        return res

    accs = [line.strip().split(";") for line in read_acc(acc_file)]
    accs = sorted(accs, key=lambda x: (x[0].casefold(), x[0]))
    if not path:
        return accs
    p_name = os.path.join(path, "pmap.mi")
    p_lines = open(p_name, "r", encoding="ascii").readlines()
    passes = [
        line.strip().split(";") for line in p_lines if not line.startswith("#")
    ]
    # Get dictionary of passwords
    pdict = dict_from_triplets(passes)
    assert pdict
    new = []
    for what, user, kpass in accs:
        if what.startswith("#"):
            continue
        expose = kpass.startswith(PASS_EXPOSE_TUPS)
        if expose:
            alist = pdict[kpass]
            assert isinstance(alist, list)
            kpass = alist[0]
        #print(":::", [what, user, kpass])
        new.append([what, user, kpass])
    return new

def dict_from_triplets(triplets) -> dict:
    """ Returns dictionary from file which has the left most column with a key.
    Additionally, checks whether the 'password' (said 'svalue') was already used by anyone already.
    """
    assert isinstance(triplets, list)
    adict = {}
    used = {}
    for trip in triplets:
        key = trip[0]
        assert key not in adict, f"Duplicate key ('{key}'): {trip}"
        adict[key] = trip[1:]
        svalue = adict[key][0]
        if svalue in used:
            print(f"Duplicate svalue '{svalue}': {trip}, used by: {used[svalue]}")
            return {}
        used[svalue] = key
    return adict

def simple_dump(out, accs:list, mis):
    tolerance = 1
    max_width = 24 + 12 + 2 + 11 + tolerance
    lines = []
    rankdict = mis.dbm["rank"].key_dict()
    for trip in accs:
        what, user, kpass = trip
        if what not in rankdict:
            continue
        if rankdict[what].startswith("0"):	# e.g. 'title;0;unused'
            continue
        assert not what.startswith(TUP_EXCLUDE), what
        hint = rankdict[what].split("=", maxsplit=1)[-1]
        hint = hint.replace(" ", "~")
        shown = f"{hint:_<24} {user:<12} {kpass:.<11}"
        alen = len(shown)
        msg = f"Too wide ({alen} vs {max_width}, kpass len={len(kpass)}): {shown}"
        assert 0 < alen <= max_width, msg
        shown = shown.replace(" " * 4, " .. ")
        lines.append(shown)
    for line in sorted(lines, key=str.casefold):
        shown = line.replace("~", " ")
        out.write(f"{shown}\n")


if __name__ == "__main__":
    main()
