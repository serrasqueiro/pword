#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" mocto2 -- Matrix with 8x8 (octogonal), with ZIP-file support

(c)2024  Henrique Moreira

Author: Henrique Moreira, h@serrasqueiro.com
"""

# pylint: disable=missing-function-docstring


from pword.ZipFile import ZipFile

_MATRIX_SQUARE = 8
_MATRIX_LINES = "ABCDEFGH"
_XY_MAX_STR_8CARD = "H8.3"
_BASIC_CARD = {
    "by-letter": {},
}


def test_main():
    MYPASSWORD = ""
    #MYPASSWORD = "myPas$word2!"	# Enter your password here if necessary
    moct = MatrixOcto8(fname="key.zip", name="myOcto", pwd=MYPASSWORD)
    #print("get_str():", moct.get_str())
    moct.builder()
    assert moct.rows["by-letter"], moct.name
    print("rows by-letter:", moct.rows["by-letter"])


class TextMatrix():
    """ Abstract class for text files
    """
    _data_str = ""
    _error = 0
    _dim = 0

    def __init__(self, name=""):
        self.name = name

    def is_ok(self) -> bool:
        """ Returns True if all ok """
        return self._error == 0

    def error_code(self) -> int:
        return self._error

    def __str__(self):
        """ string return """
        return self.get_str()

    def get_str(self) -> str:
        lista = []
        for line in self._data_str.splitlines():
            if line and line[0] in _MATRIX_LINES:
                lista.append(" ".join(line.strip().split(" ")))
        return "\n".join(lista)


class MatrixOcto8(TextMatrix):
    """ Class for textual Matrix 8x8
    """
    rows = None

    def __init__(self, data="", fname=None, pwd="", name="octo"):
        super().__init__(name)
        code = -1
        self._dim = _MATRIX_SQUARE
        self._mypass = bytes(pwd, "ascii") if pwd else None
        if data:
            assert not fname, name
            code = self._read_from_data(data)
        else:
            assert not data, "data and filename?"
            code = self._card_reader(fname, fname.endswith(".zip"))
        self._error = code
        self.rows = _BASIC_CARD

    @staticmethod
    def max_coord_str():
        return _XY_MAX_STR_8CARD

    def letters(self):
        return tuple(self.rows["by-letter"].keys())

    def get_by_letter(self, letter) -> list:
        if isinstance(letter, str):
            return self.rows["by-letter"][letter]
        if isinstance(letter, (tuple, list)):
            return [self.rows["by-letter"][alpha] for alpha in letter]
        return []

    def builder(self, debug=0) -> bool:
        """ Builds useful data-structure, and returns True if all is ok. """
        letters = _MATRIX_LINES
        if len(letters) != self._dim:
            return False
        idx, card = 0, self.get_str().splitlines()
        for letter in letters:
            there = card[idx][0]
            tense = card[idx][1:].strip().split(" ")
            dog = [numeric_tooth(num) for num in tense]
            if debug > 0:
                print(f"Letter {letter}: {dog}")
            assert there == letter
            idx += 1
            self.rows["by-letter"][letter] = dog
        return True

    def _read_from_data(self, data) -> int:
        """ Read from text string input """
        self._data_str = data
        card = self.get_str()
        is_ok = len(card.splitlines()) == self._dim
        if not is_ok:
            return 101
        return 0

    def _card_reader(self, fname, is_zip:bool) -> int:
        """ Reads either a text file or a zip-file """
        there = []
        mypass = self._mypass
        if is_zip:
            myzip = ZipFile(fname)
            there = [
                {
                    "obj": ala,
                    "path": ala.filename,
                } for ala in myzip.filelist
            ]
        if there:
            assert len(there) == 1, "zip not with single file"
            dname = there[0]["path"]
            with myzip.open(dname, pwd=mypass) as fdin:
                data = fdin.read()
            text = data.decode("ascii")
        else:
            dname = fname
            with open(fname, "r", encoding="ascii") as fdin:
                text = fdin.read()
        code = self._read_from_data(text)
        return code


def numeric_tooth(what, top_value=1000):
    """ Returns the numeric string for a 'tooth': the number within a row of a card.
    """
    fmt = "03d"
    assert isinstance(what, str)
    num = int(what)
    assert 0 <= num < top_value
    return f"{int(num):{fmt}}"


if __name__ == "__main__":
    test_main()
