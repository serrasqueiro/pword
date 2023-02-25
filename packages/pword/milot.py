# -*- coding: utf-8 -*-
#
# (c)2020..2023  Henrique Moreira
""" MiLot-like classes, for text files

Author: Henrique Moreira, h@serrasqueiro.com
"""

# pylint: disable=missing-function-docstring
# pylint: disable=consider-using-ternary, too-many-locals

import os.path
from pword import fileaccess, stable

debug_areas = ["mil", "nav"]

_MAP_NAMES = {
    "users": ("users.mi", "Users",),
    "accs": ("accs.mi", "Accounts",),
    "pmap": ("pmap.mi", "Password-map",),
    "rank": ("rank.mi", "Account rank",),	# 0 means invalid; 1 is the highest rank, 9 the lowest
}

TBL_W_UNIQUE_KEYS = (	# Tables with unique keys
    "users",
    "pmap",
)

ALT_NAMES = {
    "info": ("info.mi", "Information",),
}

TBL_BASIC_INVALID = (
    # Tables where values are more liberal,
    #	see also _invalid_chrs (e.g. ! ? ...)
    "accs",
    "rank",	# because it is keyed by the accounts ('accs')
    "info",
)

TBL_ALLOWED_VALUE_GEN = (
    "info", # values may contain ':'
)


class MiAny():
    """ Generic class for text files
    """
    # pylint: disable=no-member
    DEF_MI_NAME = "my"

    def __init__(self, name):
        assert name, "name empty"
        self.name = name
        self._db_order, self._db_alt = tuple(), tuple()
        self._ignore_case = True
        self._map_mi_to_kind = None
        self._invalid_chrs_in_value = ":"

    def __str__(self):
        return self.get_str()

    def get_order(self):
        return self._db_order


class MiLot(MiAny):
    """ Class for text '.mi' files
    """
    # _map_names = {}
    dbm = None

    def __init__(self, map_names=None, alt_tables=False, name=None):
        super().__init__(MiAny.DEF_MI_NAME if name is None else name)
        self._map_names = _MAP_NAMES if map_names is None else map_names
        assert isinstance(self._map_names, dict)
        self._process_alt = alt_tables
        self._db_order = (
            "accs", "users", "pmap",
            "rank",
        )
        self._db_alt = tuple(sorted(ALT_NAMES))

    def get_str(self) -> str:
        assert self.dbm
        res = ""
        for what in self._db_order:
            res += ";" if res else ""
            res += self._dbm_short_info(what)
        xtra = ""
        for what in self._db_alt:
            info = self.dbm.get(what)
            if info:
                xtra += ";" if xtra else ""
                xtra += self._dbm_short_info(what)
        if xtra:
            res += f";({xtra})"
        return res

    def process_path(self, path, dump_level=0, debug=0) -> int:
        """ Main path processor!
        """
        assert isinstance(path, str)
        assert int(dump_level) >= 0
        assert int(debug) >= 0
        _invalid_chrs = " :!?$*()="
        those = sorted(self._map_names)
        self._build_kinds()
        checks = [
            build_path(path,
                       self._map_names[what][0]) for what in those
        ]
        if self._process_alt:
            checks += [
                build_path(path,
                           ALT_NAMES[name][0]) for name in self._db_alt
            ]
        aprint('mil', debug, "Items:", checks)
        dbm = {}
        for one in checks:
            what = self.what_kind(one)
            aprint('mil', debug, f"Check, kind={what}: {one}")
            assert what
            if what in ("pmap",):
                tbl = stable.STableKey(one, "")
            else:
                unique = what in TBL_W_UNIQUE_KEYS
                s_val_join = ";" if what in ALT_NAMES else "="
                tbl = stable.STableKey(one, s_val_join, unique)
            if tbl.get_msg():
                print(f"Uops, STableKey(): {tbl.get_msg()}")
                return 3
            if what in TBL_BASIC_INVALID:
                is_ok = tbl.hash_key("?")
            else:
                is_ok = tbl.hash_key(_invalid_chrs)
            aprint('mil', int(debug >= 3),
                   f"STableKey({one}): "
                   f"is_ok? {is_ok} '{tbl.get_msg()}'\n{tbl.get_rows()}\n<--\n")
            if not is_ok:
                return 1
            dbm[what] = tbl
            if dump_level > 0:
                self.dump_table(tbl, what, debug)
        self.dbm = dbm
        is_ok = self.check_consistency(debug)
        return 0 if is_ok else 4

    def db_heads(self) -> list:
        res = []
        for tbl_name in self._db_order:
            tbl = self.dbm[tbl_name]
            tup = tbl.get_header()
            res.append(tup)
        return res

    def db_alt_tables(self) -> list:
        res = []
        for tbl_name in self._db_alt:
            tbl = self.dbm[tbl_name]
            res.append(tbl)
        return res

    def dump_db(self, show_pass=False, debug=0):
        assert self.dbm, self.name
        aprint('mil', debug, f"dump_db(show_pass={show_pass}): {self.name}")
        for tbl_name in self._db_order:
            tbl = self.dbm[tbl_name]
            aprint(
                'mil', debug,
                f"{tbl.get_origin_file()}: #{len(tbl.get_rows())},"
                f" {tbl.get_header()}"
            )
        for tbl_name in self._db_order:
            show = (tbl_name == "pmap" and show_pass) or tbl_name != "pmap"
            if show:
                self.dump_table(self.dbm[tbl_name], tbl_name)
        return True

    def dump_table(self, tbl, what, debug=0) -> bool:
        key, _, sname = tbl.keyval
        for k in sname:
            val = key[k]
            if what not in TBL_ALLOWED_VALUE_GEN:
                for achr in self._invalid_chrs_in_value:
                    if achr in val:
                        return False
        for k in sname:
            val = key[k]
            aprint('mil', debug, f"Key ({what}) {k}: {val}")
        if what in (
            "accs",
        ):
            for k in sname:
                val = key[k]
                print(f"Account {k}: {val}")
        else:
            for k in sname:
                val = key[k]
                print(f"Key ({what}) {k}: {val}")
        return True


    def check_consistency(self, debug=0) -> bool:
        """ Checks consistency of database
        """
        is_ok = self._check_dbm_consistency(self.dbm, debug)
        aprint('mil', debug, f"check_consistency(): is_ok? {is_ok}")
        return is_ok

    def _check_dbm_consistency(self, dbm, debug=0) -> bool:
        """ Check consistency of dbm """
        usrs = dbm.get("users")
        accs = dbm.get("accs")
        pmap = dbm.get("pmap")
        info = dbm.get("info")
        rank = dbm.get("rank")
        if not (usrs and accs and pmap):
            return False
        is_ok = self._check_triplets(
            (usrs, accs, pmap),
            (rank,),
            debug
        )
        assert is_ok
        if info:
            # Check 'info' table consistency: key (first column) must be at 'accs'
            for one in info.get_key_list():
                is_ok = one in accs.keyval[0]
                aval = info.keyval[0][one]
                if aval.startswith("F"):	# No check on 'accs'
                    continue
                # Check any upper-case match
                ups, xtra = [elem.upper() for elem in accs.keyval[0]], ""
                if one.upper() in ups:
                    xtra = " (try fix-case)"
                if not is_ok:
                    info.report_error(f"Field key '{one}' not in 'accs'{xtra}")
                    return False
        return True

    def _check_triplets(self, trip, other, debug) -> bool:
        """ Check user, accounts, and password map """
        usrs, accs, pmap = trip
        rank = other[0]
        aprint('mil', debug, "check_triplets():", rank.get_rows())
        for tbl in (usrs, accs, pmap):
            items = tbl.get_key_list()
            first = None
            for one in items:
                val = tbl.keyval[0][one]
                first = tbl.get_rows()[0][1:].strip().split(";")[0]
                aprint('mil', debug, f"file={tbl.get_origin_file()}, {first} '{one}': {val}")
            if not items:
                aprint('mil', debug, f"file={tbl.get_origin_file()}, <empty>")
        for account in accs.get_key_list():
            spl = accs.keyval[0][account].split("=")
            assert len(spl) == 2, f"spl={spl}"
            user_ref, pass_ref = spl
            a_pass = pmap.keyval[0].get(pass_ref)
            shown_user = usrs.keyval[0].get(user_ref)
            if shown_user is None:
                shown_user = "?"
            aprint('mil', debug,
                   f"account '{account}': user_ref={user_ref},"
                   f" is: {shown_user}, pass_ref={pass_ref} : {a_pass}")
            assert shown_user != "?", f"account={account} user_ref: {user_ref}"
        # All account titles listed at rank should be at accs
        lookup = accs.key_dict()
        for key in rank.get_key_list():
            assert key in lookup, f"rank: '{key}' not at accs"
            assert key in accs.get_key_list(), key	# Redundant!
            val = rank.key_dict()[key]
            assert 0 <= int(val[0]) <= 9, val
            if val.endswith("="):
                rank.key_dict()[key] = val + key
        return True

    def credentials(self, a_filter=None, show_pass="plain", if_single=True) -> list:
        """ Returns the complete list of credentials (title, (username, password))
        It yields a single result if if_single=True and a_filter matches (exactly) a single title.
        """
        assert isinstance(if_single, bool)
        alist, refs = [], []
        match = (None, None)
        #key_to, from_name, accounts = self.dbm["accs"].keyval
        key_to, _, accounts = self.dbm["accs"].keyval
        usrs, pmap = self.dbm["users"].keyval, self.dbm["pmap"].keyval
        for title in accounts:
            user_ref, pass_ref = key_to[title].split("=")
            trip = [title, (user_ref, pass_ref)]
            refs.append(trip)
        for trip in refs:
            title = trip[0]
            # convert element#1 (username, password) from other tables
            username = usrs[0][trip[1][0]]
            pass_ref = trip[1][1]
            try:
                passwd = pmap[0][pass_ref] if show_pass == "plain" else pass_ref
            except KeyError:
                passwd = "*" + pass_ref
            pair = (username, passwd)
            if self._show_title(title, a_filter):
                alist.append((title, pair))
                if a_filter is not None and title == a_filter:
                    match = (title, pair)
        if len(alist) > 1 and if_single and match[0] is not None:
            # Exact match?, only show that in this case
            res = [match]
        else:
            res = alist
        return res

    def what_kind(self, fname):
        """ Returns kind of file, e.g. 'accs', or None if not found. """
        name = os.path.basename(fname)
        return self._map_mi_to_kind.get(name)

    def _dbm_short_info(self, what) -> str:
        """ Returns the short information of table 'what'. """
        return f"{what}=#{len(self.dbm[what].get_rows())}"

    def _build_kinds(self) -> list:
        """ (Re-)builds _map_mi_to_kind """
        self._map_mi_to_kind = {}
        loads = []
        maps = [_MAP_NAMES]
        if self._process_alt:
            maps.append(ALT_NAMES)
        for adict in maps:
            loads += [(fname, kind) for kind, (fname, _) in adict.items()]
        for fname, kind in loads:
            assert fname not in self._map_mi_to_kind
            self._map_mi_to_kind[fname] = kind
        return loads

    def _show_title(self, title, a_filter) -> bool:
        if a_filter is None:
            return True
        assert isinstance(a_filter, str)
        if self._ignore_case:
            title = title.upper()
            flt = a_filter.upper()
        else:
            flt = a_filter
        if not flt:
            return True
        if title.startswith(flt):
            return True
        # Show if 'flt' within sub-string
        if flt.startswith("@"):
            flt = flt[1:]
            return flt in title
        return False


def build_path(path, rel) -> str:
    """ Returns the complete file path. """
    return fileaccess.path_join(path, rel)


def mprint(debug: int, *args) -> bool:
    """ Conditional debug print """
    if debug <= 0:
        return False
    print(*args)
    return True

def aprint(area: str, debug, *args) -> bool:
    if debug is False:
        return False
    assert area in debug_areas
    if area:
        shown = f"[{area}]"
        did = mprint(debug, shown, *args)
    else:
        did = mprint(debug, *args)
    return did


if __name__ == "__main__":
    print("Module, see pcheckers.py")
