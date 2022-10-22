#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" pcheckers configuration

Author: Henrique Moreira, h@serrasqueiro.com
"""

# pylint: disable=missing-function-docstring, unused-argument

import pword.fileaccess as fileaccess

REL_PATH = fileaccess.path_join(".config", "pcheckers")
CONFIG_NAME = "config"

DEFAULT_CONFIG = (
    "key_abs_path=$HOME/pdir",
)


def main_test():
    pconfig = PConfig()
    print("pconfig.get_path():", pconfig.get_path())
    for avar in sorted(pconfig.config(), key=str.casefold):
        there = pconfig.config()[avar]
        print(f"{avar}={there}")


def _get_home() -> str:
    """ Returns the home directory. """
    home = fileaccess.get_home()
    assert home
    return home


class AnyConfig():
    """ Any Configuration, abstract class. """
    _msgs = None
    _my_vars = {
        "HOME": _get_home(),
    }

    def get_var(self, avar):
        """ Returns variable 'avar' value. """
        return self._my_vars.get(avar)


class PConfig(AnyConfig):
    """ pcheckers configuration """
    # pylint: disable=no-self-use
    _home, _path = "", ""
    _raw, _translated = None, None

    def __init__(self, opt_home=None):
        if opt_home is None:
            home = _get_home()
        else:
            home = opt_home
        self._home = home
        self._path = fileaccess.path_join(home, REL_PATH, CONFIG_NAME)
        conf = self._read_config(self._path)
        s_msg = conf.get("msg")
        self._raw, self._translated = dict(), dict()
        if not s_msg:
            _, s_msg = self._set_config(conf)
        self._msgs = s_msg

    def get_path(self) -> str:
        """ Returns the path """
        return self._path

    def config_exists(self) -> bool:
        """ Returns True if configuration path exists. """
        return fileaccess.is_file(self._path)

    def config(self) -> dict:
        """ Returns the configuration. """
        return self._translated

    def get_config_str(self, avar, def_val="") -> str:
        """ Returns configuration of 'avar'. """
        there = self._translated.get(avar)
        if there is None:
            return def_val
        assert isinstance(there, str)
        return there

    def conf_data(self, astr) -> str:
        """ Returns the simplified string in a configuration line. """
        line = astr.strip()
        if line.startswith("#"):
            return ""
        return line

    def _read_config(self, fname, optional=True) -> dict:
        """ Reads configuration from 'fname' """
        is_ok, conf = True, dict()
        data = list()
        try:
            data = [self.conf_data(elem) for elem in open(fname, "r").readlines()]
        except FileNotFoundError:
            is_ok = False
        if not is_ok:
            data = [self.conf_data(elem) for elem in DEFAULT_CONFIG]
        for line in data:
            lrvalue = line.split("=", maxsplit=1)
            stmt = lrvalue[0].strip()
            concat = stmt.endswith("+")
            if concat:
                stmt = stmt[:-1]
            if len(lrvalue) < 2:
                if not stmt:
                    continue
                if stmt in conf:
                    return {"msg": f"Duplicate statement: {stmt}"}
                conf[stmt] = True
            else:
                aval = lrvalue[1].strip()
                there = conf.get(stmt)
                if concat:
                    if there:
                        if isinstance(there, list):
                            conf[stmt].append(aval)
                        else:
                            conf[stmt] = [there] + [aval]
                    else:
                        conf[stmt] = [aval]
                else:
                    conf[stmt] = aval
        return conf

    def _set_config(self, conf: dict) -> tuple:
        """ Sets configuration, and checks it is correct. """
        assert isinstance(conf, dict)
        is_ok, msg = True, ""
        self._raw = conf
        confs = dict()
        for key in sorted(conf):
            if not is_ok:
                break
            aval = conf[key]
            for sub in "/":
                for avar in sorted(PConfig._my_vars):
                    astr = f"${avar}{sub}"
                    newstr = aval.replace(astr, self.get_var(avar) + sub)
                    aval = newstr
            if "\\" in aval:
                aval = aval.replace("\\", "/")
            if "$" in aval:
                # At least one variable does not exist
                is_ok = False
                msg = f"Unknown var: ${aval}"
            else:
                confs[key] = aval
        if is_ok:
            self._translated = confs
        return is_ok, msg


if __name__ == "__main__":
    main_test()
