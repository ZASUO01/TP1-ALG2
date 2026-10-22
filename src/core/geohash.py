BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
INDEX = {c: i for i, c in enumerate(BASE32)}

def encode(lat, lon, precision):
    latRange = [-90.0, 90.0]
    lonRange = [-180.0, 180.0]
    
    result = []
    bits = 0
    numBits = 0
    isLon = True

    while len(result) < precision:
        interval, value = (lonRange, lon) if isLon else (latRange, lat)
        mid = (interval[0] + interval[1]) / 2
        if value >= mid:
            bits = (bits << 1) | 1
            interval[0] = mid
        else:
            bits <<= 1
            interval[1] = mid
        numBits += 1
        isLon = not isLon
        if numBits == 5:
            result.append(BASE32[bits])
            bits = 0
            numBits = 0
    return "".join(result)


def decode(geohash):
    latRange = [-90.0, 90.0]
    lonRange = [-180.0, 180.0]
    isLon = True
    
    for c in geohash:
        value = INDEX[c]
        for i in range(4, -1, -1):
            interval = lonRange if isLon else latRange
            mid = (interval[0] + interval[1]) / 2

            if (value >> i) & 1:
                interval[0] = mid
            else:
                interval[1] = mid
            
            isLon = not isLon
    return latRange, lonRange


def center(latRange, lonRange):
    return ((latRange[0] + latRange[1]) / 2, (lonRange[0] + lonRange[1]) / 2)

def neighbors(geohash):
    latRange, lonRange = decode(geohash)
    lat, lon = center(latRange, lonRange)

    dLat = latRange[1] - latRange[0]
    dLon = lonRange[1] - lonRange[0]
    
    precision = len(geohash)
    result = []
    
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue
            nLon = (lon + j * dLon + 180) % 360 - 180
            result.append(encode(lat + i * dLat, nLon, precision))
    return result
