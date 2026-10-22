from dash import Dash

from src.callbacks import registerCallbacks
from src.state import AppState
from src.ui import buildLayout

state = AppState()

def main():
    app = Dash(__name__, title="Busca por entregadores")
    app.layout = buildLayout()
    registerCallbacks(app, state)
    app.run(debug=False)

if __name__ == "__main__":
    main()
