def _intersection(a: list[int], b: list[int]) -> int:
    return sum(1 for i in range(len(a)) if a[i] == 1 and b[i] == 1)

def _union(a: list[int], b: list[int]) -> int:
    return sum(1 for i in range(len(a)) if a[i] == 1 or b[i] == 1)

def _sum_bits(v: list[int]) -> int:
    return sum(v)

def jaccard(a: list[int], b: list[int]) -> float:
    inter = _intersection(a, b)
    uni = _union(a, b)
    if uni == 0:
        return 0.0
    return inter / uni

def dice(a: list[int], b: list[int]) -> float:
    inter = _intersection(a, b)
    total = _sum_bits(a) + _sum_bits(b)
    if total == 0:
        return 0.0
    return 2.0 * inter / total

def cosine(a: list[int], b: list[int]) -> float:
    inter = _intersection(a, b)
    mag_a = _sum_bits(a)
    mag_b = _sum_bits(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return inter / (mag_a * mag_b) ** 0.5
