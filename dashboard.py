import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Carregar predições
df = pd.read_csv("reports/predicoes.txt", sep='\t')

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Mapeamento de Risco"),
    dcc.Graph(
        figure=px.density_mapbox(df, lat="latitude", lon="longitude", z="risco",
                                 radius=10, mapbox_style="open-street-map")
    ),
    html.H4("Top 10 trechos críticos"),
    html.Ul([html.Li(f"{row.latitude:.4f}, {row.longitude:.4f}: {row.risco:.2f}")
             for _, row in df.nlargest(10, 'risco').iterrows()])
])

if __name__ == '__main__':
    app.run_server(debug=True)