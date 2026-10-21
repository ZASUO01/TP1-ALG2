import dash_leaflet as dl
from dash import dcc, html

BH_CENTER = [-19.92, -43.94]
BH_BOUNDS = [[-20.06, -44.09], [-19.75, -43.84]]
MAX_COURIERS = 20000
MAX_RADIUS_KM = 20
TILES_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
TILES_ATTRIBUTION = "Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap contributors"

METRICS = [
    ("metric-found", "Entregadores no raio"),
    ("metric-min-distance", "Distância mínima"),
    ("metric-mean-distance", "Distância média"),
    ("metric-mean-eta", "Tempo médio de chegada"),
    ("metric-search-time", "Tempo de busca"),
    ("metric-generate-time", "Tempo de geração"),
]

def buildLayout():
    return html.Div(className="page", children=[
        header(),
        dcc.Loading(
            custom_spinner=loadingMessage(),
            overlay_style={"visibility": "visible", "opacity": 0.4},
            children=[
                html.Div(className="sections", children=[fleetSection(), searchSection()]),
                mapSection(),
                metricsSection(),
            ],
        ),
    ])

def header():
    return html.Header(className="header", children=[
        html.H1("Busca por entregadores"),
        html.Span("Belo Horizonte", className="subtitle"),
    ])

def loadingMessage():
    return html.Div("Carregando...", className="loading", role="status")


def field(label, inputId, component):
    return html.Div(className="field", children=[
        html.Label(label, htmlFor=inputId),
        component,
    ])


def fleetSection():
    return html.Section(className="card section", children=[
        html.H2("Entregadores"),
        html.Div(className="row", children=[
            field(
                "Número de entregadores (N)",
                "n",
                dcc.Input(id="n", type="number", min=1, max=MAX_COURIERS, step=1, value=1000),
            ),
            html.Button("Gerar", id="generate", className="button"),
        ]),
    ])


def searchSection():
    return html.Section(className="card section", children=[
        html.H2("Bares"),
        html.Div(className="row", children=[
            field(
                "Bar",
                "bar",
                dcc.Dropdown(
                    id="bar",
                    options=[],
                    placeholder="Digite o nome ou endereço do bar",
                    className="dropdown",
                ),
            ),
            field(
                "Raio (km)",
                "radius",
                dcc.Input(id="radius", type="number", min=0.1, max=MAX_RADIUS_KM, step=0.1, value=2),
            ),
            html.Button("Buscar", id="search", className="button"),
        ]),
    ])


def mapSection():
    return dl.Map(
        id="map",
        className="card map",
        center=BH_CENTER,
        zoom=13,
        minZoom=13,
        maxZoom=16,
        maxBounds=BH_BOUNDS,
        maxBoundsViscosity=1.0,
        preferCanvas=True,
        children=[
            dl.TileLayer(url=TILES_URL, attribution=TILES_ATTRIBUTION),
            dl.LayerGroup(id="couriers-layer"),
            dl.LayerGroup(id="search-layer"),
        ],
    )


def metricsSection():
    return html.Section(className="card section", children=[
        html.H2("Métricas"),
        html.Table(className="metrics", children=[
            html.Tbody([
                html.Tr([html.Th(label), html.Td("–", id=metricId)])
                for metricId, label in METRICS
            ]),
        ]),
    ])
