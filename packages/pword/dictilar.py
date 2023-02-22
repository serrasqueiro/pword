# dictilar.py  (c)2021  Henrique Moreira

""" Simplest dictionaries: show them safely, from 'table' package
"""
# pylint: disable=unused-argument

DEFAULT_END: str = "\n"

class Shown():
    """ Shown class
    """
    _data = ""
    _name = ""

    def __init__(self, name=""):
        self._name = name
        self._data = ""

    def named(self) -> str:
        """ Just the class or var name. """
        return self._name

    def string(self) -> str:
        """ Returns the build string from var. content """
        return self._data

    def __str__(self) -> str:
        """ Wrapper for string() """
        return self.string()

class DictShown(Shown):
    """ DictShown - Show dictionaries in a comfortable way
    """
    def __init__(self, adict:dict, name=""):
        aname = name
        if name == "":
            aname = adict.__class__.__name__
        super().__init__(aname)
        self._data = self._build_text(adict, end=DEFAULT_END)

    def stringify(self, value) -> str:
        """ Returns a safe string for a string, or any other variable as a string
        """
        if isinstance(value, dict):
            astr = self._build_text(value, ";", ".")
        elif isinstance(value, str):
            astr = safe_string(value)
        else:
            astr = f"{value}"
        return astr

    def _build_text(self, adict:dict, middle="\n", end="") -> str:
        astr = ""
        keys = sorted(adict, key=str.casefold)
        for key in keys:
            value = adict[key]
            if astr:
                astr += middle
            astr += f"{key}: {self.stringify(value)}"
        if astr:
            astr += end
        return astr

def safe_string(astr, quoted_empty="''") -> str:
    """ Returns a safe, readable-text string """
    if not astr:
        return f"{quoted_empty}"
    assert isinstance(astr, str)
    result = ""
    for achr in astr:
        if achr == "\n":
            result += achr
            continue
        if achr < " " or achr > "~" or achr == "\\":
            tic = "\\" + f"{ord(achr):02x}"
        else:
            tic = achr
        result += tic
    return result

# No main!
if __name__ == "__main__":
    print("Import module!")
