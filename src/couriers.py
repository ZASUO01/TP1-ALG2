import os

import geopandas as gpd
import numpy as np
import osmnx as ox
from shapely.geometry import LineString, Point

GRAPH_PATH = "cache/bh_drive.graphml"
PLACE = "Belo Horizonte, Minas Gerais, Brazil"
MAX_DISTANCE_M = 500


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


def generateCouriers(n, bars, graph, seed=None):
    rng = np.random.default_rng(seed)
    crs = graph.graph["crs"]

    anchors = bars.iloc[rng.integers(0, len(bars), n)]
    anchorPoints = gpd.GeoSeries(
        gpd.points_from_xy(anchors["longitude"], anchors["latitude"]), crs="EPSG:4326"
    ).to_crs(crs)

    angle = rng.uniform(0, 2 * np.pi, n)
    distance = MAX_DISTANCE_M * np.sqrt(rng.uniform(0, 1, n))
    x = anchorPoints.x.to_numpy() + distance * np.cos(angle)
    y = anchorPoints.y.to_numpy() + distance * np.sin(angle)

    snapped = []
    for (u, v, key), px, py in zip(ox.distance.nearest_edges(graph, x, y), x, y):
        line = edgeGeometry(graph, u, v, key)
        snapped.append(line.interpolate(line.project(Point(px, py))))
    snapped = gpd.GeoSeries(snapped, crs=crs).to_crs("EPSG:4326")

    return [(point.y, point.x, k) for k, point in enumerate(snapped)]
