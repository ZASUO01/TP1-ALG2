import math
import random

import pytest

from src.process.search import (
    KM_PER_DEGREE,
    buildIndex,
    haversine,
    precisionForRadius,
    searchRadius,
)

def randomPoints(n, seed):
    rng = random.Random(seed)
    return [
        (rng.uniform(-20.05, -19.75), rng.uniform(-44.07, -43.85), k)
        for k in range(n)
    ]


def test_haversine_known_values():
    assert haversine(-19.92, -43.94, -19.92, -43.94) == 0
    assert haversine(0, 0, 0, 1) == pytest.approx(KM_PER_DEGREE)
    assert haversine(0, 0, 1, 0) == pytest.approx(KM_PER_DEGREE)
    assert haversine(0, 0, 0, 180) == pytest.approx(math.pi * 6371.0)
    assert haversine(-19.92, -43.94, -19.85, -43.97) == pytest.approx(
        haversine(-19.85, -43.97, -19.92, -43.94)
    )


def test_precision_for_radius():
    assert precisionForRadius(0, -19.92) == 8
    assert precisionForRadius(1, -19.92) == 5
    assert precisionForRadius(10000, -19.92) == 0
    radii = [0.01, 0.1, 0.5, 1, 2, 5, 10, 50, 100, 1000]
    precisions = [precisionForRadius(r, -19.92) for r in radii]
    assert precisions == sorted(precisions, reverse=True)


def test_search_empty_index():
    trie = buildIndex([])
    assert searchRadius(trie, -19.92, -43.94, 5) == []


@pytest.mark.parametrize("radiusKm", [0.05, 0.3, 1, 2.5, 7, 40, 10000])
def test_search_matches_brute_force(radiusKm):
    points = randomPoints(3000, 1)
    trie = buildIndex(points)
    rng = random.Random(2)
    for _ in range(20):
        lat = rng.uniform(-20.05, -19.75)
        lon = rng.uniform(-44.07, -43.85)
        expected = sorted(
            p[2] for p in points if haversine(lat, lon, p[0], p[1]) <= radiusKm
        )
        result = searchRadius(trie, lat, lon, radiusKm)
        assert sorted(p[2] for _, p in result) == expected
        distances = [d for d, _ in result]
        assert distances == sorted(distances)


def test_search_finds_point_across_cell_border():
    # two points ~20 m apart on opposite sides of the cell border at lon -43.9453125
    trie = buildIndex([(-19.9248, -43.9454, "west"), (-19.9248, -43.9452, "east")])
    assert precisionForRadius(0.05, -19.9248) == 7
    result = searchRadius(trie, -19.9248, -43.9454, 0.05)
    assert sorted(p[2] for _, p in result) == ["east", "west"]
