#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" mi-files dump and edit

Author: Henrique Moreira, h@serrasqueiro.com
"""

# pylint: disable=missing-function-docstring, unused-argument

import sys
import os
from pword import dictilar
from pword.pcheckersconfig import PConfig
from pword import fileaccess
from pword.milot import MiLot, mprint


def main():
    """ Main (non-interactive) script """
    code = process(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""Usage:

python pcheckers.py [options] [path] [path...]

Options are:
  -v                Verbose (twice: -v -v, shows information too)
  -c ALL|string     Show all credentials, or names starting with 'string'.

  -p (or --show-path) shows current configuration path (and optionally config).
""")
    sys.exit(code if code else 0)


def process(out, err, args):
    opts = {
        "verbose": 0,
        "cred": None,
        "replica": None,
        "similar": True,
        "config": "",
    }
    key_local_path = False
    param = args
    while param and param[0].startswith("-"):
        if param[0].startswith("-v"):
            opts["verbose"] += param[0].count("v")
            del param[0]
            continue
        if param[0] in ("-c", "--cred"):
            if len(param) < 2:
                return None
            opts["cred"] = param[1] if param[1] != "ALL" else ""
            del param[:2]
            continue
        if param[0] in ("-r", "--replica"):
            opts["replica"] = param[1]
            del param[:2]
            continue
        if param[0] in ("-p", "--show-path"):
            opts["config"] = "show-path"
            del param[0]
            continue
        if param[0] in ("-k", "--key-current-dir"):
            del param[0]
            key_local_path = True
            continue
        return None
    if opts["cred"] and opts["replica"]:
        return None	# one option, or the other, not both!

    pconf = PConfig()
    if opts["config"] == "show-path":
        if param[1:]:
            return None
        print("Config. path:", pconf.get_path())
        is_ok = pconf.config_exists()
        if not is_ok:
            err.write(f"File not found: {pconf.get_path()}\n")
            return 2
        if opts["verbose"]:
            adict = pconf.config()
            astr = dictilar.DictShown(adict)
            print(f"--\n{astr}", end='')
        return 0
    apath = pconf.get_config_str("key_abs_path")	# key_abs_path=/.../...
    if key_local_path:
        apath = os.getcwd()
    if not param:
        param = [apath] if apath else ["."]
        if opts["verbose"]:
            print("Using path:", param[0])
    if opts["cred"] is not None:
        hit = opts["cred"]
        msg = f"No 'cred' found, similar to: '{hit}'\nUse '-c ALL' to show all!\n"
        mis, creds = show_credentials(param, opts)
        code = 0 if mis else 4
        if code:
            assert creds, "Expected that no creds were found!"
            err.write(f"Bogus (error-code {code}), msg: {creds[0]}\n")
        else:
            if not creds:
                code = 2
                err.write(msg)
    elif opts["replica"]:
        if len(param) > 1:
            return None
        code = do_replica(out, err, opts["replica"], param)
    else:
        code = do_it(out, err, param, opts)
    return code


def do_it(out, err, param, opts) -> int:
    assert param
    verbose = opts["verbose"]
    debug = int(verbose >= 3)
    dump_pass = 1 if verbose else 0
    mprint(debug, f"do_it(): opts={opts}, debug={debug}")
    mis = new_milot()
    for path in param:
        code = mis.process_path(path, debug=debug)
        if code != 0:
            err.write(f"Check mi-files failed: error-code {code}\n")
            if mis.dbm:
                print(f"Keys read: {mis.dbm.keys()}")
    if mis.dbm:
        mis.dump_db(dump_pass)
    #info = mis.db_alt_tables()[0]
    if verbose > 0:
        is_ok = mis.dump_table(mis.dbm["info"], "info")
        assert is_ok
        print("MiLot get_str():", mis.get_str())
        print("db_heads():", mis.db_heads())
    return code


def do_replica(out, err, dest, param) -> int:
    """ Do a replica and make it read-only! """
    if not fileaccess.is_dir(dest):
        err.write(f"Replica is not a directory: {dest}\n")
        return 3
    mis = new_milot()
    path = param[0]
    code = mis.process_path(path)
    if code != 0:
        return 1
    print("Doing replica...", dest)
    repl = [(mis.dbm[what].get_origin_file(), what) for what in sorted(mis.dbm)]
    pairs = []
    for source, what in repl:
        dpath = fileaccess.path_join(dest, what+".mi")
        pairs.append((source, dpath))
        is_ok = fileaccess.is_file(dpath) and fileaccess.file_permission_read(dpath)
        if not is_ok:
            err.write(f"Could not find destination: {dpath}\n")
            return 4
    datas, destdir = {}, ""
    for source, dpath in pairs:
        data = open(source, "r", encoding="ascii").read()
        datas[source] = (data, fileaccess.get_file_time(source)[:2])
        destdir = fileaccess.dirname(dpath)
    for source, dpath in pairs:
        fileaccess.change_permission(destdir)
        data, tup_time = datas[source]
        can_write = fileaccess.file_permission_write(dpath)
        s_xtra = "" if can_write else " (changing write-access)"
        print("Copying", source, f"to {dpath}{s_xtra}")
        fileaccess.change_permission(dpath)
        with open(dpath, "wb") as fout:
            fout.write(data.encode("ISO-8859-1"))
        fileaccess.change_permission(dpath, "r")
        fileaccess.set_file_time(dpath, tup_time)
        if out:
            out.write(f"Access now: {fileaccess.file_stat_octstr(dpath)} {dpath}\n")
    if destdir:
        fileaccess.change_permission(destdir, "r", best_effort=True)
    return 0


def show_credentials(param, opts, out=True):
    verbose = opts["verbose"]
    debug = int(verbose >= 3)
    mprint(debug, f"show_credentials(): opts={opts}, debug={debug}")
    a_filter, similar = opts["cred"], opts["similar"]
    mis = new_milot()
    if verbose > 0:
        print("Show credentials, filter:", a_filter if a_filter else "ALL")
    for path in param:
        code = mis.process_path(path, debug=debug)
        if code:
            return None, [f"Bogus path: '{path}'"]
    creds, tries = best_matches(mis, a_filter, similar, debug)
    if not out:
        return mis, creds
    info = mis.dbm["info"]
    for title, cred in creds:
        if verbose > 0:
            print(f"{title}: {cred[0]} {cred[1]}")
            lookup = info.keyval[0].get(title)
            if verbose >= 2 and lookup:
                print("INFO:", lookup)
            print("--")
        else:
            print(f"{title:_<20.19} {cred[0]} {cred[1]}")
    if not creds:
        if verbose:
            print("Tried:", sorted(tries))
    return mis, creds

def best_matches(mis, a_filter, similar, debug=0) -> tuple:
    """ If similar is 'True', it returns all gathered data. """
    creds = []
    tries = {}
    for idx, sbst in enumerate(
        (None, ".", " ", "-", "_"),
        1
    ):
        if sbst is None:
            flt = a_filter
        else:
            flt = a_filter.replace(sbst, " ")
        creds = mis.credentials(flt)
        if not flt:
            return creds, tries
        shown = creds if len(creds) < 3 else (creds[:2] + ["..."])
        if debug > 0:
            print(f"\n# best_matches(idx={idx}): credentials({repr(flt)}): {shown}")
        if not creds and not similar:
            break
        if flt in tries:
            continue
        tries[flt] = idx	# Indicate the index of replacement (only the first matching)
        if creds:
            return creds, tries
    return creds, tries

def new_milot():
    """ Returns new instance of table dbm.
    """
    return MiLot(alt_tables=True)


if __name__ == "__main__":
    main()
