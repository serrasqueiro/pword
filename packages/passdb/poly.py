""" Polynomial CRCs """

class CRC32:
    """ CRC-32 (IEEE 802.3) """
    POLY = 0xEDB88320

    def __init__(self):
        self._crc = 0xFFFFFFFF

    def update(self, data: bytes):
        for b in data:
            self._crc ^= b
            for _ in range(8):
                self._crc = (self._crc >> 1) ^ (self.POLY if (self._crc & 1) else 0)

    def digest(self) -> int:
        return (~self._crc) & 0xFFFFFFFF

    def hexdigest(self) -> str:
        return f"{self.digest():08X}"

    @classmethod
    def compute(cls, s: str) -> int:
        c = cls()
        c.update(s.encode("ascii"))
        return c.digest()

    @classmethod
    def compute_hex(cls, s: str) -> str:
        return f"{cls.compute(s):08X}"
