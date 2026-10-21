import geopandas as gpd
import networkx as nx
import pandas as pd
import pytest

from src.couriers import MAX_DISTANCE_M, generateCouriers

CRS = "EPSG:31983"  # SIRGAS 2000 / UTM 23S, covers Belo Horizonte
STREET_Y = 7796000.0
BAR_X = 609000.0


def oneStreetGraph():
    # a single straight east-west street, 4 km long, in projected meters
    graph = nx.MultiDiGraph(crs=CRS)
    graph.add_node(1, x=BAR_X - 2000, y=STREET_Y)
    graph.add_node(2, x=BAR_X + 2000, y=STREET_Y)
    graph.add_edge(1, 2, key=0)
    return graph


def oneBar():
    point = gpd.GeoSeries(gpd.points_from_xy([BAR_X], [STREET_Y + 100]), crs=CRS)
    point = point.to_crs("EPSG:4326")
    return pd.DataFrame({"latitude": point.y, "longitude": point.x})


def toProjected(couriers):
    return gpd.GeoSeries(
        gpd.points_from_xy([c[1] for c in couriers], [c[0] for c in couriers]),
        crs="EPSG:4326",
    ).to_crs(CRS)


@pytest.mark.parametrize("n", [0, 1, 50])
def test_generates_n_couriers(n):
    couriers = generateCouriers(n, oneBar(), oneStreetGraph(), seed=1)
    assert len(couriers) == n
    assert [c[2] for c in couriers] == list(range(n))


def test_couriers_are_on_the_street_near_the_bar():
    couriers = generateCouriers(200, oneBar(), oneStreetGraph(), seed=1)
    points = toProjected(couriers)
    assert points.y.to_numpy() == pytest.approx(STREET_Y, abs=0.01)
    assert (abs(points.x.to_numpy() - BAR_X) <= MAX_DISTANCE_M + 0.01).all()


def test_same_seed_same_couriers():
    a = generateCouriers(20, oneBar(), oneStreetGraph(), seed=7)
    b = generateCouriers(20, oneBar(), oneStreetGraph(), seed=7)
    c = generateCouriers(20, oneBar(), oneStreetGraph(), seed=8)
    assert a == b
    assert a != c
