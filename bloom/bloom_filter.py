import math
import hashlib
import struct


class BloomFilter:
    def __init__(self, size, hash_functions=None):
        self.size = size
        #  Hafsa to replace with hash_functions.create_hashes(k)
        self.hash_functions = hash_functions if hash_functions is not None else self._default_hashes(7)
        self._byte_count = (size + 7) // 8
        self._bits = bytearray(self._byte_count)
        self.count = 0

    @classmethod
    def for_capacity(cls, expected_items, fp_rate=0.01, hash_functions=None):
        target = fp_rate * 0.9
        m = int(-expected_items * math.log(target) / (math.log(2) ** 2))
        k = round((m / expected_items) * math.log(2))
        return cls(m, hash_functions or cls._default_hashes(k))

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
        # Hafsa: each hf will be a function from hash_functions.py
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

    def save(self, path):
        k = len(self.hash_functions)
        with open(path, 'wb') as f:
            f.write(struct.pack('<III', self.size, k, self.count))
            f.write(self._bits)

    @classmethod
    def load(cls, path, hash_functions=None):
        with open(path, 'rb') as f:
            size, k, count = struct.unpack('<III', f.read(12))
            bf = cls.__new__(cls)
            bf.size = size
            bf.hash_functions = hash_functions if hash_functions is not None else cls._default_hashes(k)
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
