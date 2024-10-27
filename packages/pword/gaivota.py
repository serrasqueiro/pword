# -*- coding: utf-8 -*-

""" gaivota.py -- working with base32

Base 32 alphabet:
	/1/	https://datatracker.ietf.org/doc/html/rfc4648.html#section-6
"""

# Other
#	/20/	https://pypi.org/project/english-words/	# english words (Python module)
#	/21/	https://svnweb.freebsd.org/base/head/share/dict/web2?view=markup&pathrev=326913	# web2 rev.

import base64

ALT_ENC = "iso-8859-1"	# aka Latin-1

STD_BASE32_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"	# /1/
CUS_BASE32_ALPHA = "1234567@ABCDEFGHJKLMNPQRSTUVWXYZ"	# My own alpha

def main():
    """ Simple testing! """
    tests = {
        "Gaivota": "Seagul",
        b'Co\xc3\xa7a'.decode("utf-8"): "Scratches",
    }
    for word, meaning in tests.items():
        input_string = word
        encoded = string_to_base32(input_string)
        print(f"Base32 encoded ({meaning}):", encoded)
        new, msg = base32_to_string(encoded, "1")
        if msg:
            print("Bogus:", msg)
        else:
            if new.isalnum():
                print("Back string:", new)
                assert input_string == new, meaning
            else:
                print("Coded for:", meaning)
            #open(meaning + ".txt", "wb").write((new + "\n").encode(ALT_ENC))
        print("--\n")
    #assert base64._b32alphabet.decode("ascii") == STD_BASE32_ALPHA
    assert STD_BASE32_ALPHA == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', "What? (1)"


def string_to_base32(astr:str, use_encode="utf-8") -> str:
    """ Encode the string into bytes """
    byte_data = astr.encode(use_encode)
    # Convert the bytes to Base32
    base32_encoded = base64.b32encode(byte_data)
    # Decode the Base32 bytes back to a string
    return base32_encoded.decode(use_encode)

def base32_to_string(bstr:str, use_encode="ascii"):
    """ Convert base32 to string, returns None if decode is not possible.
    """
    if use_encode == "1":
        use_encode = "iso-8859-1"
    octets = base64.b32decode(bstr)
    msg, new = "", "?"
    try:
        new = octets.decode(use_encode)
    except UnicodeDecodeError as err:
        msg = f"Unable to decode: {err}"
    return new, msg

# Main tests
if __name__ == "__main__":
    main()
