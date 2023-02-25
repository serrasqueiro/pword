# -*- coding: utf-8 -*-
""" mocto -- Matrix with 8x8 (octogonal)

Author: Henrique Moreira, h@serrasqueiro.com
"""

# pylint: disable=missing-function-docstring


_MATRIX_SQUARE = 8
_MATRIX_LINES = "ABCDEFGH"
_XY_MAX_STR_8CARD = "H8.3"
_BASIC_CARD = {
    "by-letter": {},
}


class MatrixAny():
    """ Generic class for text files
    """
    _data_str = ""
    _error = 0
    _dim = 0

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


class MatrixOcto(MatrixAny):
    """ Class for textual Matrix 8x8
    """
    rows = None

    def __init__(self, data="", fname=None):
        code = -1
        self._dim = _MATRIX_SQUARE
        if data:
            assert not fname
            code = self._read_from_data(data)
        else:
            code = self._read_from_data(open(fname, "r", encoding="ascii").read())
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
        return list()

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


def numeric_tooth(what, top_value=1000):
    """ Returns the numeric string for a 'tooth': the number within a row of a card.
    """
    fmt = "03d"
    assert isinstance(what, str)
    num = int(what)
    assert 0 <= num < top_value
    return f"{int(num):{fmt}}"


if __name__ == "__main__":
    print("Module, import me!")
