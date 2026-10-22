import os

import osmnx as ox

GRAPH_PATH = "cache/bh_drive.graphml"
PLACE = "Belo Horizonte, Minas Gerais, Brazil"


def loadStreetGraph():
    if os.path.exists(GRAPH_PATH):
        graph = ox.load_graphml(GRAPH_PATH)
    else:
        graph = ox.graph_from_place(PLACE, network_type="drive")
        ox.save_graphml(graph, GRAPH_PATH)
    return ox.project_graph(graph)
