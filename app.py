import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# ------------------------------------------------
# APP INITIALIZATION
# ------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG]
)


# ------------------------------------------------
# DISTRICT DEFINITIONS
# ------------------------------------------------

districts = [
    "Kampala",
    "Wakiso",
    "Mukono",
    "Mpigi",
    "Mityana",
    "Luweero",
    "Masaka",
    "Jinja"
]

district_centers = {
    "Kampala": (0.3476, 32.5825),
    "Wakiso": (0.4044, 32.4599),
    "Mukono": (0.3533, 32.7553),
    "Mpigi": (0.2250, 32.3136),
    "Mityana": (0.4175, 32.0228),
    "Luweero": (0.8400, 32.4800),
    "Masaka": (-0.3338, 31.7341),
    "Jinja": (0.4244, 33.2042)
}


# ------------------------------------------------
# DATA GENERATION FUNCTION
# ------------------------------------------------

def generate_data():

    customers = []
    claims = []
    hospitals = []

    customer_id = 1
    claim_id = 1
    hospital_id = 1

    for district in districts:

        lat_center, lon_center = district_centers[district]

        # customers
        for i in range(40):

            customers.append({
                "customer_id": f"CUST{customer_id}",
                "district": district,
                "lat": lat_center + np.random.randn()*0.02,
                "lon": lon_center + np.random.randn()*0.02
            })

            customer_id += 1

        # claims
        for i in range(15):

            cost = np.random.randint(100000, 5000000)

            claims.append({
                "claim_id": f"CLM{claim_id}",
                "customer_id": f"CUST{np.random.randint(1, customer_id)}",
                "cost": cost,
                "district": district,
                "lat": lat_center + np.random.randn()*0.02,
                "lon": lon_center + np.random.randn()*0.02
            })

            claim_id += 1

        # hospitals
        for i in range(3):

            hospitals.append({
                "hospital_id": f"HSP{hospital_id}",
                "name": f"Hospital {hospital_id}",
                "district": district,
                "lat": lat_center + np.random.randn()*0.01,
                "lon": lon_center + np.random.randn()*0.01
            })

            hospital_id += 1

    return (
        pd.DataFrame(customers),
        pd.DataFrame(claims),
        pd.DataFrame(hospitals)
    )


# ------------------------------------------------
# DASHBOARD LAYOUT
# ------------------------------------------------

app.layout = dbc.Container(fluid=True, children=[

    html.H2(
        "Insurance Geospatial Intelligence Dashboard",
        style={
            "textAlign": "center",
            "margin": "15px",
            "color": "white"
        }
    ),

    dcc.Interval(
        id="refresh",
        interval=5000,
        n_intervals=0
    ),

    dbc.Row([

        # ------------------------------------
        # CONTROL PANEL
        # ------------------------------------

        dbc.Col([

            html.Label(
                "Map Layers",
                style={"color": "white", "fontWeight": "bold"}
            ),

            dcc.Checklist(
                id="layer_toggle",
                options=[
                    {"label": "Customers", "value": "customers"},
                    {"label": "Claims", "value": "claims"},
                    {"label": "Hospitals", "value": "hospitals"},
                    {"label": "Risk Zones", "value": "risk"},
                    {"label": "Coverage Gap", "value": "gap"}
                ],
                value=["customers", "claims", "hospitals"],
                labelStyle={
                    "display": "block",
                    "color": "white",
                    "fontSize": "15px",
                    "padding": "3px"
                }
            ),

            html.Br(),

            html.Label(
                "District Filter",
                style={"color": "white", "fontWeight": "bold"}
            ),

            dcc.Dropdown(
                id="district_filter",
                options=[{"label": d, "value": d} for d in districts],
                placeholder="All Districts"
            ),

            html.Br(),

            dbc.Card(dbc.CardBody(html.H4(id="clients")), className="mb-2"),
            dbc.Card(dbc.CardBody(html.H4(id="claims")), className="mb-2"),
            dbc.Card(dbc.CardBody(html.H4(id="avg")), className="mb-2"),
            dbc.Card(dbc.CardBody(html.H4(id="total_cost")), className="mb-2"),
            dbc.Card(dbc.CardBody(html.H4(id="claim_rate")), className="mb-2"),

        ], width=3),

        # ------------------------------------
        # MAP + CHART AREA
        # ------------------------------------

        dbc.Col([

            dcc.Graph(
                id="map",
                style={"height": "70vh"}
            ),

            dcc.Graph(id="region_chart")

        ], width=9)

    ])

])


# ------------------------------------------------
# DASH CALLBACK
# ------------------------------------------------

@app.callback(

[
Output("map", "figure"),
Output("clients", "children"),
Output("claims", "children"),
Output("avg", "children"),
Output("total_cost", "children"),
Output("claim_rate", "children"),
Output("region_chart", "figure")
],

[
Input("refresh", "n_intervals"),
Input("layer_toggle", "value"),
Input("district_filter", "value")
]

)

def update_dashboard(n, layers, district):

    customers, claims, hospitals = generate_data()

    if district:

        customers = customers[customers.district == district]
        claims = claims[claims.district == district]
        hospitals = hospitals[hospitals.district == district]

    total_clients = len(customers)
    total_claims = len(claims)

    avg_cost = int(claims.cost.mean()) if total_claims > 0 else 0
    total_cost = int(claims.cost.sum())

    claim_rate = round(total_claims / total_clients, 2) if total_clients > 0 else 0

    fig = go.Figure()

    if "customers" in layers:

        fig.add_trace(go.Scattermapbox(
            lat=customers.lat,
            lon=customers.lon,
            mode="markers",
            marker=dict(size=6, color="cyan"),
            name="Customers",
            customdata=customers[["customer_id", "district"]],
            hovertemplate=
            "<b>Customer</b><br>"
            "ID: %{customdata[0]}<br>"
            "District: %{customdata[1]}"
            "<extra></extra>"
        ))

    if "claims" in layers:

        fig.add_trace(go.Scattermapbox(
            lat=claims.lat,
            lon=claims.lon,
            mode="markers",
            marker=dict(size=9, color="red"),
            name="Claims",
            customdata=claims[["claim_id", "customer_id", "cost"]],
            hovertemplate=
            "<b>Claim</b><br>"
            "Claim ID: %{customdata[0]}<br>"
            "Customer: %{customdata[1]}<br>"
            "Amount: UGX %{customdata[2]:,}"
            "<extra></extra>"
        ))

    if "hospitals" in layers:

        fig.add_trace(go.Scattermapbox(
            lat=hospitals.lat,
            lon=hospitals.lon,
            mode="markers",
            marker=dict(size=12, color="lime"),
            name="Hospitals",
            customdata=hospitals[["name", "district"]],
            hovertemplate=
            "<b>Hospital</b><br>"
            "Name: %{customdata[0]}<br>"
            "District: %{customdata[1]}"
            "<extra></extra>"
        ))

    fig.update_layout(

        mapbox=dict(
            style="carto-darkmatter",
            zoom=8,
            center=dict(lat=0.3476, lon=32.5825)
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01
        ),

        margin=dict(l=0, r=0, t=0, b=0)

    )

    region_counts = claims["district"].value_counts()

    region_fig = go.Figure()

    region_fig.add_bar(
        x=region_counts.index,
        y=region_counts.values
    )

    region_fig.update_layout(
        template="plotly_dark",
        title="Claims by District"
    )

    return (

        fig,
        f"Total Clients: {total_clients}",
        f"Total Claims: {total_claims}",
        f"Average Claim Cost: UGX {avg_cost:,}",
        f"Total Claim Cost: UGX {total_cost:,}",
        f"Claim Rate: {claim_rate}",
        region_fig

    )


# ------------------------------------------------
# RUN SERVER
# ------------------------------------------------
server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)

