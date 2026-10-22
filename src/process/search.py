import math

from src.core.geohash import encode, neighbors
from src.core.trie import CompactTrie

EARTH_RADIUS_KM = 6371.0
KM_PER_DEGREE = EARTH_RADIUS_KM * math.pi / 180
MAX_PRECISION = 8

def haversine(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dPhi = math.radians(lat2 - lat1)
    dLambda = math.radians(lon2 - lon1)
    a = math.sin(dPhi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dLambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, a)))


def cellSize(precision):
    totalBits = 5 * precision
    lonBits = (totalBits + 1) // 2
    latBits = totalBits // 2
    return 180 / 2 ** latBits, 360 / 2 ** lonBits


def precisionForRadius(radiusKm, lat):
    for precision in range(MAX_PRECISION, 0, -1):
        dLat, dLon = cellSize(precision)
        farthestLat = min(90.0, abs(lat) + dLat)
        heightKm = dLat * KM_PER_DEGREE
        widthKm = dLon * KM_PER_DEGREE * math.cos(math.radians(farthestLat))
        if heightKm >= radiusKm and widthKm >= radiusKm:
            return precision
    return 0


def buildIndex(points):
    trie = CompactTrie()
    for point in points:
        lat, lon = point[0], point[1]
        trie.insert(encode(lat, lon, MAX_PRECISION), point)
    return trie


def searchRadius(trie, lat, lon, radiusKm):
    precision = precisionForRadius(radiusKm, lat)
    if precision == 0:
        candidates = trie.search("")
    else:
        cell = encode(lat, lon, precision)
        candidates = []
        for prefix in [cell] + neighbors(cell):
            candidates.extend(trie.search(prefix))

    result = []
    for point in candidates:
        distance = haversine(lat, lon, point[0], point[1])
        if distance <= radiusKm:
            result.append((distance, point))
    result.sort(key=lambda pair: pair[0])
    return result
