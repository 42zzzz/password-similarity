import math
import hashlib
import struct


class BloomFilter:
    def __init__(self, size, hash_functions=None):
        self.size = size
        self.hash_functions = hash_functions if hash_functions is not None else self._default_hashes(3)
        self._byte_count = (size + 7) // 8
        self._bits = bytearray(self._byte_count)
        self.count = 0

    @staticmethod
    def _default_hashes(num):
        def _make(salt_byte):
            def h(item):
                h_obj = hashlib.sha256()
                h_obj.update(struct.pack('<B', salt_byte))
                h_obj.update(item.encode('utf-8'))
                return int.from_bytes(h_obj.digest(), 'big')
            return h
        return [_make(i) for i in range(num)]

    def _indices(self, item):
        return [hf(item) % self.size for hf in self.hash_functions]

    def add(self, item):
        for i in self._indices(item):
            self._bits[i >> 3] |= 1 << (i & 7)
        self.count += 1

    def check(self, item):
        for i in self._indices(item):
            if not (self._bits[i >> 3] & (1 << (i & 7))):
                return False
        return True

    @property
    def false_positive_rate(self):
        if self.count == 0:
            return 0.0
        k = len(self.hash_functions)
        n = self.count
        m = self.size
        return (1.0 - math.exp(-k * n / m)) ** k
