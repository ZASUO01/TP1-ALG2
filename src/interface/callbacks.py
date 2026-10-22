from dash import Input, Output, ctx
from dash.exceptions import PreventUpdate

from src.interface.ui import METRICS, couriersLayer, metricValues, searchLayer


def registerCallbacks(app, state):
    @app.callback(
        Output("bar", "options"),
        Input("url", "pathname"),
    )
    def loadData(_):
        state.load()
        return state.barOptions()

    @app.callback(
        Input("n", "value"),
    )
    def updateN(n):
        state.n = n

    @app.callback(
        Output("couriers-layer", "data"),
        Output("search-layer", "children"),
        Output("couriers-table", "data"),
        *[Output(metricId, "children") for metricId, _, _, _ in METRICS],
        Input("generate", "n_clicks"),
        Input("bar", "value"),
        Input("radius", "value"),
        prevent_initial_call=True,
    )
    def updateMap(_, barIndex, radiusKm):
        if not state.loaded:
            raise PreventUpdate
        if ctx.triggered_id == "generate" and state.n:
            state.generate()

        state.barIndex = barIndex
        state.radiusKm = radiusKm
        state.search()

        return (
            couriersLayer(state.couriers, state.foundIds()),
            searchLayer(state.selectedBar(), state.radiusKm),
            state.foundRows(),
            *metricValues(state.metrics()),
        )
