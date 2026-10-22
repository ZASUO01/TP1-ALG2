import time

import pandas as pd

from src.couriers import generateCouriers, loadStreetGraph
from src.search import buildIndex
from src.trie import CompactTrie

BARS_PATH = "data/bares_geo.csv"

class AppState:
    def __init__(self):
        self.bars = None
        self.graph = None
        self.couriers = []
        self.trie = CompactTrie()

        self.n = 1000
        self.barIndex = None
        self.radiusKm = 2.0

        self.found = []
        self.searchTimeMs = None
        self.generateTimeS = None

    @property
    def loaded(self):
        return self.bars is not None and self.graph is not None

    def load(self):
        if self.loaded:
            return
        self.bars = pd.read_csv(BARS_PATH)
        self.graph = loadStreetGraph()

    def generate(self):
        start = time.perf_counter()
        self.couriers = generateCouriers(self.n, self.bars, self.graph)
        self.trie = buildIndex(self.couriers)
        self.found = []
        self.generateTimeS = time.perf_counter() - start

    def barOptions(self):
        names = self.bars["NOME_FANTASIA"].fillna(self.bars["NOME"])
        addresses = (
            self.bars["DESC_LOGRADOURO"] + " " + self.bars["NOME_LOGRADOURO"]
            + ", " + self.bars["NUMERO_IMOVEL"].astype(str)
            + " - " + self.bars["NOME_BAIRRO"]
        )
        return [
            {"label": f"{name} ({address})", "value": index}
            for index, name, address in zip(self.bars.index, names, addresses)
        ]

    def selectedBar(self):
        if self.barIndex is None:
            return None
        return self.bars.loc[self.barIndex]
