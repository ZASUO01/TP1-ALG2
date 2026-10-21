from dash import Dash
from src.ui import buildLayout


def main():
    app = Dash(__name__, title="Busca por entregadores")
    app.layout = buildLayout()
    app.run(debug=False)


if __name__ == "__main__":
    main()
