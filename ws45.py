
###### TO DO:
# Generate GeoJSON for countries across the years (1945-)
# for sub-country: ISO-2 or ISO-3 codes. See https://pypi.org/project/iso3166-2/
# awesome GeoJSON resource: https://icr.ethz.ch/data/cshapes/CShapes-2.0.geojson 


from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import json
from datetime import datetime, timedelta
import geopandas as gpd

geojson_data = json.load(open('data/CShapes-2.0.geojson'))

def filter_geojson_by_year(geojson_data, year, month = 1, day = 1):
    this_gj = [ f for f in geojson_data["features"] if datetime(f["properties"]["gwsyear"],f["properties"]["gwsmonth"],f["properties"]["gwsday"]) <= datetime(year,month,day) <= datetime(f["properties"]["gweyear"],f["properties"]["gwemonth"],f["properties"]["gweday"]) ]
    geo_df = gpd.GeoDataFrame.from_features(this_gj).set_index('cntry_name')
    # geo_df["fill_color"] = "rgba(0,0,0,0)"
    return geo_df #{"type": "FeatureCollection", "features": this_gj}

firstYear = 1886 # 1945
lastYear = 2019 # 2016

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        html.H3('Country-wise history'),
                        html.P(""),
                        html.H5("Projection"),
                        dcc.RadioItems(
                            id='projection-selector',
                            options=[{'label': ' Equirectangular', 'value': 'equirectangular'},
                                    {'label': ' Orthographic', 'value': 'orthographic'},
                                    {'label': ' Natural Earth', 'value': 'natural earth'},
                                    {'label': ' Mercator', 'value': 'mercator'},],
                            value="equirectangular",
                            inline=False),
                        html.P(""),
                        html.H5("Scope"),
                        dcc.RadioItems(
                            id='scope-selector',
                            options=[{'label': ' World', 'value': 'world'},
                                    {'label': ' Europe', 'value': 'europe'},
                                    {'label': ' Asia', 'value': 'asia'},
                                    {'label': ' Africa', 'value': 'africa'},
                                    {'label': ' North America', 'value': 'north america'},
                                    {'label': ' South America', 'value': 'south america'},],
                            value="world",
                            inline=False),
                    ]),
                    width=2  # Takes up 2 out of 12 columns in Bootstrap grid
                ),
                dbc.Col(
                    html.Div([
                        html.P('Year'),
                        dcc.Slider(
                            id='year-slider',
                            min=firstYear,
                            max=lastYear,
                            step=1,
                            value=1970,
                            marks={str(year): str(year) for year in [firstYear,lastYear] },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        dcc.Graph(id="choropleth-maps-x-graph"),
                    ]),
                    width=10  # Takes up 10 out of 12 columns in Bootstrap grid
                ),
            ]
        )
    ],
    fluid=True  # Makes the container span the full width
)

@app.callback(
    Output("choropleth-maps-x-graph", "figure"),
    Input("projection-selector", "value"),
    Input("year-slider", "value"),
    Input("scope-selector", "value"),
)
def display_choropleth(projection,year,scope):
    fig = go.Figure(go.Scattergeo())
    geo_df = filter_geojson_by_year(geojson_data, year)
    fig = px.choropleth(
        geo_df, 
        geojson=geo_df.geometry, 
        scope=scope,
        locations=geo_df.index, #"cntry_name",
        hover_name=geo_df.index, 
        color_discrete_sequence=['rgba(0, 0, 0, 0)'],
        )
    fig.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    fig.update_geos(
        visible=True,
        showcountries=False,
        showsubunits=False,
        showland=True,
        showframe=True,
        showlakes=False,
        # fitbounds="locations",  # optional, forces zoom to your shapes
        resolution=50,
        projection_type=projection,
    )
    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#  def display_choropleth(projection):
#     fig = go.Figure(go.Scattergeo())
#     fig.update_geos(
#         visible=False, resolution=50,
#         showcountries=True, countrycolor="gray"
#     )
#     fig.update_geos(projection_type=projection)
#     fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
#     return fig

    # df = px.data.election() # replace with your own data source
    # geojson = px.data.election_geojson()
    # fig = px.choropleth(
    #     df, geojson=geojson, color=candidate,
    #     locations="district", featureidkey="properties.district",
    #     projection="mercator", range_color=[0, 6500])
    # fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # return fig


if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
