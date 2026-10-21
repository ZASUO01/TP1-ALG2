import pytest

from src.geohash import decode, center, encode, neighbors

BH_POINTS = [
    (57.64911, 10.40744),  
    (-19.9245, -43.9352), 
    (-19.8512, -43.9706),  
    (0.0, 0.0),
    (-33.8688, 151.2093),
]


def test_encode_known_values():
    assert encode(57.64911, 10.40744, 11) == "u4pruydqqvj"
    assert encode(42.6, -5.6, 5) == "ezs42"
    assert encode(0.0, 0.0, 5) == "s0000"


def test_decode_known_value():
    latRange, lonRange = decode("ezs42")
    assert latRange == [42.5830078125, 42.626953125]
    assert lonRange == [-5.625, -5.5810546875]

    lat, lon = center(latRange, lonRange)

    assert lat == pytest.approx(42.605, abs=1e-3)
    assert lon == pytest.approx(-5.603, abs=1e-3)

@pytest.mark.parametrize("lat, lon", BH_POINTS)
@pytest.mark.parametrize("precision", [1, 5, 7, 9, 12])
def test_round_trip(lat, lon, precision):
    gh = encode(lat, lon, precision)
    assert len(gh) == precision
    latRange, lonRange = decode(gh)
    assert latRange[0] <= lat <= latRange[1]
    assert lonRange[0] <= lon <= lonRange[1]


@pytest.mark.parametrize("lat, lon", BH_POINTS)
@pytest.mark.parametrize("precision", [3, 6, 9])
def test_neighbors(lat, lon, precision):
    gh = encode(lat, lon, precision)
    nbs = neighbors(gh)
    assert len(nbs) == 8
    assert len(set(nbs)) == 8
    assert gh not in nbs
    assert all(len(n) == precision for n in nbs)

    latRange, lonRange = decode(gh)
    lat0, lon0 = center(latRange, lonRange)

    dLat = latRange[1] - latRange[0]
    dLon = lonRange[1] - lonRange[0]
    offsets = set()
    for n in nbs:
        latRangeN, lonRangeN =  decode(n)
        latN, lonN = center(latRangeN, lonRangeN)

        di = round((latN - lat0) / dLat)
        dj = round((lonN - lon0) / dLon)
        assert latN - lat0 == pytest.approx(di * dLat)
        assert lonN - lon0 == pytest.approx(dj * dLon)
        offsets.add((di, dj))
    expected = {(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)} - {(0, 0)}
    assert offsets == expected
