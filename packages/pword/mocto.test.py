#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Matrix 8x8 (octogonal) reader; lib: mocto.py

Author: Henrique Moreira, h@serrasqueiro.com
"""

import sys
from pword.mocto import MatrixOcto

# pylint: disable=missing-function-docstring


def main():
    """ Main run """
    code = run_main(sys.stdout, sys.argv[1:])
    if code is None:
        print(f"""{__file__} command [options]

cat           Show card (cat = catalog)
""")
    sys.exit(0 if code is None else code)


def run_main(out, args):
    """ Args parser, run command! """
    code = 0
    if not args:
        return None
    cmd = args[0]
    param = args[1:]
    if cmd == "cat":
        if not param:
            print("At least one card (text-file)!\n")
            return None
        path = param[0]
        other = param[1:]
        code = run_cat(out, path, other)
    return code


def run_cat(out, path, param) -> int:
    """ shows card """
    assert out
    code = 0
    data = open(path, "r").read()
    octo = MatrixOcto(data)
    if octo.is_ok():
        code = show_par(octo, param)
    else:
        print(f"{path}: error-code {octo.error_code()}")
    return code

def show_par(octo, param, debug=0):
    """ Show card, with whatever params user has asked to.
    """
    max_card_str = MatrixOcto.max_coord_str()
    if debug > 0:
        print(f">>>\n{octo}\n<<<")
    #print(f"show_par() is_ok? {is_ok}")
    is_ok = octo.builder()
    if not is_ok:
        return 1
    if param:
        for one in param:
            if len(one) != len(max_card_str) or one[2] != ".":
                print(f"Unexpected string '{one}'; example: {max_card_str}")
                return 3
            seq = one.replace(".", "")
            letter, tooth, digit = seq[0], int(seq[1]), int(seq[2])
            if debug > 0:
                print(f"Debug: {letter}{tooth}.{digit}, seq={seq}")
            num = octo.get_by_letter(letter)[tooth-1][digit-1]
            print(one, num)
    else:
        print("Letters:", octo.letters())
        for letter in octo.letters():
            print(letter, " ".join(octo.get_by_letter(letter)))
        #print("ALL:", octo.get_by_letter(octo.letters()))
    return 0


if __name__ == "__main__":
    main()
