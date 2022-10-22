# -*- coding: utf-8 -*-
""" fileaccess -- OS-independent primitives

Author: Henrique Moreira, h@serrasqueiro.com, (c) 2021  Henrique Moreira
"""

# pylint: disable=missing-function-docstring, unused-argument

import os
import stat

AVOID_BACKSLASH = True


def get_home(default_str="") -> str:
    home = os.environ.get("HOME")
    if home is None:
        home = os.environ.get("USERPROFILE")
    if home is None:
        return default_str
    return home

def path_join(name1: str, *names) -> str:
    """ Returns the joined path, slash-based. """
    assert isinstance(name1, str)
    astr = os.path.join(name1, *names)
    if AVOID_BACKSLASH:
        return astr.replace("\\", "/")
    return astr

def is_dir(path: str) -> bool:
    return os.path.isdir(path)

def is_file(path: str) -> bool:
    return os.path.isfile(path)

def dirname(path: str) -> str:
    return os.path.dirname(path)

def file_permission_read(fname: str) -> bool:
    is_ok = os.access(fname, os.R_OK)
    return is_ok

def file_permission_write(fname) -> bool:
    is_ok = os.access(fname, os.W_OK)
    return is_ok

def change_permission(fname, to_write="w", best_effort=True) -> int:
    """ Changes file 'fname' permissions. """
    isdir = is_dir(fname)
    usr_rw = stat.S_IRUSR | stat.S_IWUSR
    perm = 0
    # what not:  ... | stat.S_IRWGRP | stat.S_IRWOTH
    if to_write == "w":
        # octal 600 (0o600) is S_IRUSR | S_IWUSR
        perm = stat.S_IRWXU if isdir else usr_rw
    elif to_write == "r":
        perm = (stat.S_IRUSR | stat.S_IXUSR) if isdir else stat.S_IRUSR
    try:
        os.chmod(fname, perm)
    except PermissionError:
        perm = -1
    pnow = file_stat(fname)
    # f"{pnow & 0o777:>4o}" = ' 666' on regular files write-able by user, group, and others!
    if not best_effort:
        raise RuntimeError("Cannot change permission of: {}".
                           format(fname))
    return pnow

def file_stat(path) -> int:
    """ Returns file/ dir unix status. """
    perm = stat.S_IMODE(os.lstat(path).st_mode)
    assert isinstance(perm, int)
    return perm

def file_stat_octstr(path) -> str:
    perm = file_stat(path)
    return f"{perm & 0o777:>03o}"

def get_file_time(path) -> tuple:
    tup = (os.lstat(path).st_atime, os.lstat(path).st_mtime, os.lstat(path).st_ctime)
    return tup

def set_file_time(path, tup) -> bool:
    if isinstance(tup, (tuple, list)):
        access_time, modif_time = tup
    elif isinstance(tup, (int, float)):
        stamp = tup
        access_time, modif_time = int(stamp), int(stamp)
    else:
        return False
    os.utime(path, (access_time, modif_time))
    return True

# File permissions in stats:
#	tups = [(name, f"0o{eval('stat.'+name):03o}" if isinstance(eval('stat.'+name), int) \
#         else '?') for name in dir(stat) if name.startswith("S_")]

if __name__ == "__main__":
    print("Please import pword.fileaccess !")
