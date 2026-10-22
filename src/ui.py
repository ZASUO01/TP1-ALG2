import dash_leaflet as dl
from dash import dash_table, dcc, html

BH_CENTER = [-19.92, -43.94]
BH_BOUNDS = [[-20.06, -44.09], [-19.75, -43.84]]
MAX_COURIERS = 20000
MAX_RADIUS_KM = 20
COURIER_COLOR = "#78909c"
HIGHLIGHT_COLOR = "#d32f2f"
TILES_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
TILES_ATTRIBUTION = "Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap contributors"

METRICS = [
    ("metric-found", "Entregadores no raio", "found", "{:d}"),
    ("metric-min-distance", "Distância mínima", "minDistanceKm", "{:.2f} km"),
    ("metric-mean-distance", "Distância média", "meanDistanceKm", "{:.2f} km"),
    ("metric-mean-eta", "Tempo médio de chegada", "meanEtaMin", "{:.1f} min"),
    ("metric-search-time", "Tempo de busca", "searchTimeMs", "{:.3f} ms"),
    ("metric-generate-time", "Tempo de geração", "generateTimeS", "{:.2f} s"),
]

def buildLayout():
    return html.Div(className="page", children=[
        dcc.Location(id="url"),
        header(),
        dcc.Loading(
            custom_spinner=loadingMessage(),
            overlay_style={"visibility": "visible", "opacity": 0.4},
            children=[
                html.Div(className="sections", children=[fleetSection(), searchSection()]),
                html.Div(className="map-row", children=[mapSection(), couriersTableSection()]),
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
            dl.GeoJSON(
                id="couriers-layer",
                data=couriersLayer([]),
                pointToLayer={"variable": "couriers.pointToLayer"},
            ),
            dl.LayerGroup(id="search-layer"),
        ],
    )


def couriersLayer(couriers, highlighted=frozenset()):
    # highlighted couriers go last so they are drawn on top
    ordered = sorted(couriers, key=lambda courier: courier[2] in highlighted)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "color": HIGHLIGHT_COLOR if courierId in highlighted else COURIER_COLOR,
                    "tooltip": f"Entregador {courierId}",
                },
            }
            for lat, lon, courierId in ordered
        ],
    }


def searchLayer(bar, radiusKm):
    if bar is None:
        return []
    center = [bar["latitude"], bar["longitude"]]
    layers = []
    if radiusKm and radiusKm > 0:
        layers.append(dl.Circle(
            center=center,
            radius=radiusKm * 1000,
            color=HIGHLIGHT_COLOR,
            weight=2,
            fillOpacity=0.05,
            interactive=False,
        ))
    layers.append(dl.CircleMarker(
        center=center,
        radius=10,
        color="#ffffff",
        weight=3,
        fillColor=HIGHLIGHT_COLOR,
        fillOpacity=1,
        children=dl.Tooltip(bar["NOME_FANTASIA"] if isinstance(bar["NOME_FANTASIA"], str) else bar["NOME"]),
    ))
    return layers


def couriersTableSection():
    return html.Section(className="card section couriers-table", children=[
        html.H2("Entregadores no raio"),
        dash_table.DataTable(
            id="couriers-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Dist. (km)", "id": "distanceKm"},
                {"name": "Tempo (min)", "id": "etaMin"},
            ],
            data=[],
            virtualization=True,
            fixed_rows={"headers": True},
            style_table={"height": "calc(60vh - 70px)", "overflowY": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "6px 8px",
                "fontFamily": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
                "fontSize": "0.85rem",
            },
            style_header={
                "fontWeight": 600,
                "color": "#616e7c",
                "backgroundColor": "#ffffff",
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_as_list_view=True,
        ),
    ])


def metricsSection():
    return html.Section(className="card section", children=[
        html.H2("Métricas"),
        html.Table(className="metrics", children=[
            html.Tbody([
                html.Tr([html.Th(label), html.Td("–", id=metricId)])
                for metricId, label, _, _ in METRICS
            ]),
        ]),
    ])


def metricValues(metrics):
    return [
        "–" if metrics[key] is None else fmt.format(metrics[key])
        for _, _, key, fmt in METRICS
    ]
