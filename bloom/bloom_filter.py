import math
import struct

from hash.hash_functions import create_hashes


class BloomFilter:
    def __init__(self, size, hash_functions=None):
        self.size = size
        self.hash_functions = hash_functions if hash_functions is not None else create_hashes(7)
        self._byte_count = (size + 7) // 8
        self._bits = bytearray(self._byte_count)
        self.count = 0

    @classmethod
    def for_capacity(cls, expected_items, fp_rate=0.01, hash_functions=None):
        target = fp_rate * 0.9
        m = int(-expected_items * math.log(target) / (math.log(2) ** 2))
        k = round((m / expected_items) * math.log(2))
        return cls(m, hash_functions or create_hashes(k))

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

    FORMAT_VERSION = 1

    def save(self, path):
        k = len(self.hash_functions)
        with open(path, 'wb') as f:
            f.write(struct.pack('<BIII', self.FORMAT_VERSION, self.size, k, self.count))
            f.write(self._bits)

    @classmethod
    def load(cls, path, hash_functions=None):
        with open(path, 'rb') as f:
            ver, size, k, count = struct.unpack('<BIII', f.read(13))
            if ver != cls.FORMAT_VERSION:
                raise ValueError(f'Unsupported format version {ver}')
            bf = cls.__new__(cls)
            bf.size = size
            bf.hash_functions = hash_functions if hash_functions is not None else create_hashes(k)
            bf._byte_count = (size + 7) // 8
            bf._bits = bytearray(bf._byte_count)
            f.readinto(bf._bits)
            bf.count = count
            return bf

    @property
    def false_positive_rate(self):
        if self.count == 0:
            return 0.0
        k = len(self.hash_functions)
        n = self.count
        m = self.size
        return (1.0 - math.exp(-k * n / m)) ** k
