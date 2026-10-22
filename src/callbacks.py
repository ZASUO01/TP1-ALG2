from dash import Input, Output, no_update

from src.ui import couriersLayer


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
        Input("bar", "value"),
        Input("radius", "value"),
    )
    def updateChoices(n, barIndex, radiusKm):
        state.n = n
        state.barIndex = barIndex
        state.radiusKm = radiusKm

    @app.callback(
        Output("couriers-layer", "data"),
        Output("metric-generate-time", "children"),
        Input("generate", "n_clicks"),
        prevent_initial_call=True,
    )
    def generate(_):
        if not state.loaded or not state.n:
            return no_update, no_update
        state.generate()
        return couriersLayer(state.couriers), f"{state.generateTimeS:.2f} s"
