import os
import math

from bloom.bloom_filter import BloomFilter


DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'top10k_rockyou.txt')
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'top10k_rockyou.blm')


def load_passwords(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [l.strip() for l in f if l.strip()]


def print_stats(bf, total):
    k = len(bf.hash_functions)
    m = bf.size
    n = bf.count
    fpr = bf.false_positive_rate
    print(f'Loaded {total} banned passwords | '
          f'm={m} bits ({m/8/1024:.1f} KB) | '
          f'k={k} hashes | '
          f'n={n} inserted | '
          f'FP rate ~{fpr*100:.2f}%')
    print()


def build_or_load():
    use_cache = os.path.exists(CACHE_FILE) and os.path.getmtime(CACHE_FILE) >= os.path.getmtime(DATA_FILE)
    if use_cache:
        bf = BloomFilter.load(CACHE_FILE)
        total = bf.count
        return bf, total

    passwords = load_passwords(DATA_FILE)
    bf = BloomFilter.for_capacity(len(passwords), fp_rate=0.01)
    for pw in passwords:
        bf.add(pw)
    bf.save(CACHE_FILE)
    return bf, len(passwords)


def main():
    if not os.path.exists(DATA_FILE):
        print(f'Error: {DATA_FILE} not found')
        return

    bf, total = build_or_load()

    print()
    print('=== Bloom Filter Password Checker ===')
    print_stats(bf, total)

    while True:
        try:
            pw = input('Enter a password (or "quit"): ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if pw.lower() == 'quit':
            break

        if not pw:
            continue

        if bf.check(pw):
            print('  -> BANNED (matches a known compromised password)\n')
        else:
            print('  -> SAFE (not found in filter)\n')

    print('Goodbye.')


if __name__ == '__main__':
    main()
