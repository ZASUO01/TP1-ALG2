import os

import geopandas as gpd
import numpy as np
import osmnx as ox
from shapely.geometry import LineString, Point

GRAPH_PATH = "cache/bh_drive.graphml"
PLACE = "Belo Horizonte, Minas Gerais, Brazil"
SIGMA_M = 300
MAX_CENTERS = 100


def loadStreetGraph():
    if os.path.exists(GRAPH_PATH):
        graph = ox.load_graphml(GRAPH_PATH)
    else:
        graph = ox.graph_from_place(PLACE, network_type="drive")
        ox.save_graphml(graph, GRAPH_PATH)
    return ox.project_graph(graph)


def edgeGeometry(graph, u, v, key):
    data = graph.edges[u, v, key]
    if "geometry" in data:
        return data["geometry"]
    nodes = graph.nodes
    return LineString([(nodes[u]["x"], nodes[u]["y"]), (nodes[v]["x"], nodes[v]["y"])])


def centerCount(n):
    return max(1, min(n // 10, MAX_CENTERS))


def generateCouriers(n, bars, graph, seed=None):
    rng = np.random.default_rng(seed)
    crs = graph.graph["crs"]

    k = min(centerCount(n), len(bars))
    centers = bars.iloc[rng.choice(len(bars), size=k, replace=False)]
    perCenter = np.full(k, n // k)
    perCenter[: n % k] += 1
    anchors = centers.iloc[np.repeat(np.arange(k), perCenter)]
    anchorPoints = gpd.GeoSeries(
        gpd.points_from_xy(anchors["longitude"], anchors["latitude"]), crs="EPSG:4326"
    ).to_crs(crs)

    x = anchorPoints.x.to_numpy() + rng.normal(0, SIGMA_M, n)
    y = anchorPoints.y.to_numpy() + rng.normal(0, SIGMA_M, n)

    snapped = []
    for (u, v, key), px, py in zip(ox.distance.nearest_edges(graph, x, y), x, y):
        line = edgeGeometry(graph, u, v, key)
        snapped.append(line.interpolate(line.project(Point(px, py))))
    snapped = gpd.GeoSeries(snapped, crs=crs).to_crs("EPSG:4326")

    return [(point.y, point.x, courierId) for courierId, point in enumerate(snapped)]
