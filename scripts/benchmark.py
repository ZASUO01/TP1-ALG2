import random
import time

import pandas as pd

from src.couriers import generateCouriers, loadStreetGraph
from src.geohash import encode, neighbors
from src.search import buildIndex, haversine, precisionForRadius, searchRadius

BARS_PATH = "data/bares_geo.csv"
SIZES = [1000, 10000, 100000]
RADII_KM = [0.5, 1, 2, 5]
QUERIES = 100
SEED = 42


def bruteForce(points, lat, lon, radiusKm):
    result = []
    for point in points:
        distance = haversine(lat, lon, point[0], point[1])
        if distance <= radiusKm:
            result.append((distance, point))
    result.sort(key=lambda pair: pair[0])
    return result


def countCandidates(trie, lat, lon, radiusKm):
    precision = precisionForRadius(radiusKm, lat)
    if precision == 0:
        return len(trie.search(""))
    cell = encode(lat, lon, precision)
    return sum(len(trie.search(prefix)) for prefix in [cell] + neighbors(cell))


def main():
    bars = pd.read_csv(BARS_PATH)
    graph = loadStreetGraph()
    rng = random.Random(SEED)
    queries = [
        (row.latitude, row.longitude)
        for row in bars.sample(n=QUERIES, random_state=SEED).itertuples()
    ]

    print("| N | radius (km) | precision | avg candidates | avg found | trie (ms) | brute force (ms) | speedup |")
    print("|---|---|---|---|---|---|---|---|")
    for n in SIZES:
        couriers = generateCouriers(n, bars, graph, seed=rng.randrange(2**32))
        start = time.perf_counter()
        trie = buildIndex(couriers)
        buildMs = (time.perf_counter() - start) * 1000
        print(f"<!-- N={n}: index built in {buildMs:.0f} ms -->")

        for radiusKm in RADII_KM:
            trieTime = bruteTime = 0.0
            candidates = found = 0
            for lat, lon in queries:
                start = time.perf_counter()
                result = searchRadius(trie, lat, lon, radiusKm)
                trieTime += time.perf_counter() - start

                start = time.perf_counter()
                expected = bruteForce(couriers, lat, lon, radiusKm)
                bruteTime += time.perf_counter() - start

                assert sorted(p[2] for _, p in result) == sorted(p[2] for _, p in expected)
                candidates += countCandidates(trie, lat, lon, radiusKm)
                found += len(result)

            trieMs = trieTime / QUERIES * 1000
            bruteMs = bruteTime / QUERIES * 1000
            print(
                f"| {n} | {radiusKm} | {precisionForRadius(radiusKm, -19.92)} "
                f"| {candidates / QUERIES:.0f} | {found / QUERIES:.0f} "
                f"| {trieMs:.2f} | {bruteMs:.2f} | {bruteMs / trieMs:.0f}x |"
            )


if __name__ == "__main__":
    main()
