# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from pandas import DataFrame
import pathlib
import dash
import requests

#Required for googlemaps API to work
import dash_leaflet as dl
from dash.dependencies import Output, Input

#Import Libraries for Chorolpeth map
import json
import numpy as np
import pandas as pd
import plotly.express as px
import os

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("./data").resolve()

#--------------------------------------------------------------------------------
# colours


history = "rgb(179,205,227)"










#--------------------------------------------------------------------------------

# Map of Japan Code

#import geojson data. This will be used for generation of map
with open(DATA_PATH.joinpath("japan_prefectures.geojson"), encoding="utf8") as f:
    data = json.load(f)
                                    
#This creates a dictionary which maps ID to states inside the geojson data
prefec_id = {}

# Populating the dictionary to contain values for prefecture id
for feature in data['features']:
    feature['id'] = feature['properties']['id_1']
    prefec_id[feature['properties']['name_1']] = feature['id']

# Import asset values for Japan by prefrecture
origindf = pd.read_csv(DATA_PATH.joinpath("Japan_Values_By_Prefrectures.csv"))
df = origindf.copy()

#Using the populated library, input a new column called 'id'
df['id'] = df['Prefrecture'].apply(lambda x: prefec_id[x])

# Create a log scale for value such that the visualisation will make sense
df['Asset_Value_Scale']=np.log10(df['value'])

# Create the map
fig=px.choropleth_mapbox(df,
                    locations="id",
                    geojson=data,
                    color="Asset_Value_Scale",
                    hover_name= "Prefrecture",
                    hover_data=['value'],
                    mapbox_style='carto-darkmatter',
                    center={'lat':36.2048,'lon':138.2529},
                    color_continuous_scale=px.colors.diverging.BrBG,
                    zoom = 3
                )

fig.update_layout(
    title_text="Visualisation of Asset spread across Japanese Prefectures", title_x=0.5,
    coloraxis_colorbar=dict(
    title="Log(Asset Values)")
    )

#--------------------------------------------------------------------------------


# Showing data for asset in table form
order_df = df.sort_values("Prefrecture")

fig_table = go.Figure(data=[go.Table(
    header=dict(values=[['<b>Prefectures</b>'],
                  ['<b>Asset Value(USD)</b>']],
                fill_color='paleturquoise'),
    cells=dict(values=[order_df.Prefrecture, order_df.value],
               fill_color='lavender'))
])
 
fig_table.update_layout(
    title_text="Asset Table",title_x=0.5
    )

#--------------------------------------------------------------------------------
# Dictionary that contains { prefecture : value } Used for the calculating of damage
pv_list = df[df.columns[0:2]]

pv_list = pv_list.values.tolist()
# New list to reformat data for conversion
convert_list = []
for i in pv_list:
    convert_list.append(i[0])
    convert_list.append(i[1])
    
# list to dictionary function
def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

pv_dict = Convert(convert_list)


# Dictionary that contains our research details 
damages_dict = {"1":0.000000289999574029004,
                "2":0.00000210249382342509,
                "3":0.0000152430578297972,
                "4":0.000110512006938516,
                "5":0.000801210873431501}       

#--------------------------------------------------------------------------------
# data to count number of cyclones a year + number of cyclones in each cat/year
jcpc_origin = pd.read_csv(DATA_PATH.joinpath("japan_cyclones_prefs_and_cat.csv"))
jcpc_df = jcpc_origin.copy()

# Data for historical tropical cyclones in Japan
line_df = pd.read_csv(DATA_PATH.joinpath("japan_2000to2020_prefs.csv"))

# Data used for DropDownBar
checking_dict = {}
historical_dmg_df_dict = {}
historical_dmg_df = jcpc_df.copy()
historical_dmg_df = historical_dmg_df[['SEASON',"NAME","SID","Highest Cat in JP"]]

historical_dmg_list = historical_dmg_df.values.tolist()
for i in historical_dmg_list:
    if i[0] not in historical_dmg_df_dict:
        historical_dmg_df_dict[i[0]] = [[i[1],i[2],i[3]]]
        checking_dict[i[2]] = i[1]
        
    else:
        if i[2] not in checking_dict:
            historical_dmg_df_dict[i[0]].append([i[1],i[2],i[3]])
            checking_dict[i[2]] = i[1]


#--------------------------------------------------------------------------------
# Meteorlogical information
precep_df = pd.read_csv(DATA_PATH.joinpath("precepitation_10_japan_prefrectures_2000_2020.csv"))
temp_df = pd.read_csv(DATA_PATH.joinpath("temperature_10_japan_prefrectures_2000_2020.csv"))


#--------------------------------------------------------------------------------
# this block of code is used in multiple callbacks
jcpc = jcpc_df.copy()
jcpc = jcpc[["SID","SEASON","Highest Cat in JP"]]
counting_dict = {}
year_count_dict = {}
jcpc_list = jcpc.values.tolist()

for i in jcpc_list:
    if i[0] not in counting_dict:
        counting_dict[i[0]] = [i[1],i[2]]
        
for i in counting_dict:
    if counting_dict[i][0] not in year_count_dict:
        year_count_dict[counting_dict[i][0]] = 1
    else:
        year_count_dict[counting_dict[i][0]] += 1
        
        
year_count_df = pd.DataFrame(list(year_count_dict.items()),columns = ['Year','Number of Cyclones']) 

#--------------------------------------------------------------------------------
# this block of code is required for the leaflet map
cor = {'Lat':[''],'Lon':['']}
MAP_ID = "map"
MARKER_GROUP_ID = "marker-group"
COORDINATE_CLICK_ID = "coordinate-click-id"



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#                                                   MAIN APPLCATION CODE

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def build_banner():
    return        html.Div(
            [
                html.Div(
                    [
                                html.H3(
                                    "SMUXCredit Suisse")
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Typhoon Risk Analysis Dashboard",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Developed by Team Cycovid-20", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("SMU School of Information Systems", id="learn-more-button"),
                            href="https://sis.smu.edu.sg/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )
def historical_panel():
    # Deck in a row in one div + 3 figs in seperate div
    return html.Div(


        children=[                            


                html.Div([

                    html.Label(["Select a Year", 
                        dcc.Dropdown(
                                id='year-dropdown',
                                options=[{'label': k, 'value': k} for k in historical_dmg_df_dict.keys()],
                                value=2000,
                                placeholder="Select a Year",
                                style={'float': 'right','width':'100%'})],style={'float': 'right','width':'100%'}),

                    html.Label(["Select a Category", 
                        dcc.Dropdown(id='cat_dropdown',
                                    options=[
                                        {'label': '1', 'value': 1},
                                        {'label': '2', 'value': 2},
                                        {'label': '3', 'value': 3},
                                        {'label': '4', 'value': 4},
                                        {'label': '5', 'value': 5}],
                                    value = 1,
                                    placeholder="Select a Category",
                                        style={'float': 'right','width':'100%'})],style={'float': 'right','width':'100%'}),
                    html.Label(["Select a Typhoon to Visualise", 
                        dcc.Dropdown(id='cyclones_dropdown',
                                    placeholder="Select a Typhoon",
                                    style={'float': 'right','width':'100%'})],style={'float': 'right','width':'100%'})
                
                ],style=dict(display='flex',backgroundColor= "white"),className="pretty_container row"),
            
                html.Div([
            # This is meant for the 3 visualisations historical , simulated and damages
                # Chunk for Scoping into a specific cyclone 
                    html.Div([
                        html.Div([
                            html.H6(id="selected_cyclone",
                                    className="control_label",),
                            dcc.Graph(id='single_line_fig')]),
                            # Chunk for visualising Historical Data
                            ],className = "four columns"),
                    html.Div([
                        html.H6(id="all_cyclones",
                                className="control_label",),
                        dcc.Graph(id='line_fig')
                    ]
                    ,className = "four columns"),

                    # Shows damage from cyclone
                    html.Div([html.H6(id="dmg_for_cyclone",
                                className="control_label",),
                                 dcc.Graph(id='dmg'),
                                  ],className = "four columns"),

                ],style=dict(display='flex',backgroundColor= "white"),className="pretty_container row"),


        ],className="tweleve columns")

def cards():
    return  html.Div([
                html.Div(
                    [html.H6(id="total_in_year_count"), html.P(id="total_in_year_string")],
                    id="total_in_year",style={'float': 'right','width':'100%',"backgroundColor": "white"},
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="catone"), html.P("Category 1")],
                    id="cat1",style={'float': 'right','width':'100%',"backgroundColor":  "white"},
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="cattwo"), html.P("Category 2")],
                    id="cat2",style={'float': 'right','width':'100%',"backgroundColor": "white"},
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="catthree"), html.P("Category 3")],
                    id="cat3",style={'float': 'right','width':'100%',"backgroundColor": "white"},
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="catfour"), html.P("Category 4")],
                    id="cat4",style={'float': 'right','width':'100%',"backgroundColor": "white"},
                    className="mini_container",
                ),
                html.Div(
                    [html.H6(id="catfive"), html.P("Category 5")],
                    id="cat5",style={'float': 'right','width':'100%',"backgroundColor": "white"},
                    className="mini_container",
                ),                                
         ],className="row container-display")

app = dash.Dash(meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])



app.layout = html.Div([
                        # This Portion of the app will show the Historical representation of past cyclones
                        html.Div(
                        id="big-app-container",
                        children=[
                            build_banner()
                        ]),

                        html.Div(
                            [html.H2("Understanding Past Typhoons",style={
                                'font-weight': 'bold'
                            }),
                            html.H4("Selecting a Year and Category provides a list of Typhoons to visualise")
                            ],
                            className="pretty_container row",
                            style={
                                'backgroundColor' : "#19D3F3"
                            }
                        ),
# ------------------------------------------------------------------------------ Climate and Asset Overview ---------------------------------------------------------------------------------------------
                        # This is meant for the deck

                        html.Div([
                        historical_panel()]),
                        html.Div([
                        cards()]),

                        html.Div(
                            [html.H2("Asset and Climate overview",style={
                                'font-weight': 'bold'
                            }),
                            html.H4("Data of asset value per prefecture + Overview of past 20 Years Climate data averaged from a sample of 10 Prefectures")
                            ],
                            className="pretty_container row",
                            style={
                                'backgroundColor' : "#00CC96"
                            }
                        ),

                        



                        # Chunk for Choropleth Map Asset Visualisation + Asset Table + Meteorological data

                            html.Div([     html.H5("Spread of Assets Across Prefectures in Japan",
                                            className="",style={'text-align': 'center'}),
                            # Chunk for Choropleth Map Assets
                                    html.Div([
                                        html.Div([

                                                    dcc.Graph(figure=fig)
                                                ],className="six columns",style={'backgroundColor': 'white'}),
                                        # Chunk for Meterological Dta
                                        html.Div([
                                                        dcc.Graph(figure=fig_table)
                                                    ],className="six columns")
                                    ],className="row",style=dict(display='flex',backgroundColor='white'))


                                ],className="pretty_container",style=dict(backgroundColor='white')),
                            

                           
  

                            # Chunk for Asset Table






                            html.Div([
                                html.Div([
                                    html.H5("Meteorological Data of japan 2000-2020 against Prefecture (Averaged from Sample of 10 Prominent Prefectures)",
                                    className="control_label",style={'text-align': 'center'}),
                                    html.Label(["Select/Remove Prefectures to view average Temperature & Precipitation of selected prefectures", 
                                        dcc.Dropdown(
                                            id='drop',
                                            options=[
                                                {'label': 'Tokyo', 'value': 'Tokyo'},
                                                {'label': 'Yokohama', 'value': 'Yokohama'},
                                                {'label': 'Osaka', 'value': 'Osaka'},
                                                {'label': 'Fukushima', 'value': 'Fukushima'},
                                                {'label': 'Aomori', 'value': 'Aomori'},
                                                {'label': 'Chiba', 'value': 'Chiba'},
                                                {'label': 'Kyoto', 'value': 'Kyoto'},
                                                {'label': 'Akita', 'value': 'Akita'},
                                                {'label': 'Nagano', 'value': 'Nagano'},
                                                {'label': 'Fukui', 'value': 'Fukui'}
                                            ],
                                            value=['Tokyo', 'Yokohama','Osaka','Fukushima','Aomori','Chiba','Kyoto','Akita','Nagano','Fukui'],
                                            multi=True
                                        )
                                        ])
                                    ]),
                                html.Div([

                                    dcc.Graph(id='meteor')
                                ],style={'backgroundColor': 'white'})

                            ],className="pretty_container row",style={'backgroundColor': 'white'}),







# ------------------------------------------------------------------------------Dont touch above ---------------------------------------------------------------------------------------------

                        
                        html.Div(
                            [html.H2("Risk Analysis of Prefectures by years",style={
                                'font-weight': 'bold'
                            }),
                            html.H4("Selecting a Prefecture on the map will trigger an analysis table showing the number of Typhoons it has eperienced from 2000 - 2020")
                            ],
                            className="pretty_container row",
                            style={
                                'backgroundColor' : "#EF553B"
                            }
                        ),

                        # Chunk for choropleth of number of events a year + click event to simulate
                        html.Div([
                            # Chunk for choropleth map of events
                            html.Div([
                                      html.Div([ 
                                        dcc.Graph(id='korro_fig')
                                      ]),
                                      html.Div([  
                                          html.Label(["Select a Year to visualise then click on a prefecture above",
                                            dcc.Dropdown(
                                                id='korro_year-dropdown',
                                                options=[{'label': k, 'value': k} for k in historical_dmg_df_dict.keys()],
                                                value=2000,
                                                style={'float': 'right','width':'100%'})],style={'float': 'right','width':'100%'})
                                      ], style=dict(display='flex'))
                                    ],className="six columns"),
                            # Chunk for viz upon click 
                            html.Div([
                                        dcc.Graph(id='click-data'),
                                    ], className='six columns')
                        ], style=dict(display='flex',backgroundColor= "white"),className="pretty_container row"),

# ------------------------------------------------------------------------------Dont touch above ---------------------------------------------------------------------------------------------




                        html.Div(
                            [html.H2("Typhoon Simulation",style={
                                'font-weight': 'bold'
                            }),
                            html.H4("Points selected on the map will be visualised below. For the most accurate damage values, the points showing the path of Typhoon should be tightly spaced")
                            ],
                            className="pretty_container row",
                            style={
                                'backgroundColor' : "#FFA15A"
                            }
                        ),






                        # This will show a huge map for the simulation
                        html.Div([
                            dl.Map(style={'width': '1700px', 'height': '500px'},
                                center=[36.73008022131222,139.57030949592613],
                                zoom=5,
                                dragging=False,
                                scrollWheelZoom=False,
                                children=[
                                    dl.TileLayer(url="http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}"),
                                    dl.LayerGroup(id=MARKER_GROUP_ID)
                                ], id=MAP_ID),
                            html.P("Coordinate (click on map):",style={
                                'font-weight': 'bold'
                            }),
                            html.Div(id=COORDINATE_CLICK_ID)],className="pretty_container tweleve columns"),


# ------------------------------------------------------------------------------Dont touch above ---------------------------------------------------------------------------------------------

                        # This will show the coordinates table , simulation of chosen points and damages incurred
                        html.Div([


                            # This chunk is for the Coordinates Table
                            html.Div([html.H6("Damages Incurred"),
                                        dcc.Graph(id='cor_table')
                                    ],className="four columns"),


                            # This chunk is for the simulation
                            html.Div([
                                        # Buttons stored inside another div
                                        html.Div([
                                            html.Button('Remove Last Point', id='btn-nclicks-1', n_clicks=0, style=dict(width="100%")),
                                            html.Button('Clear all Points', id='btn-nclicks-2', n_clicks=0, style=dict(width="100%")),
                                            html.Button('Simulate Damage', id='btn-nclicks-3', n_clicks=0, style=dict(width="100%")),
                                            dcc.Dropdown(id='sim_cat_dropdown',
                                                            options=[
                                                                {'label': 'Category 1', 'value': 1},
                                                                {'label': 'Category 2', 'value': 2},
                                                                {'label': 'Category 3', 'value': 3},
                                                                {'label': 'Category 4', 'value': 4},
                                                                {'label': 'Category 5', 'value': 5}], value=1,
                                                                style={'float': 'right','width':'100%'})
                                            ], style=dict(display='flex')),
                                        # Simulation Graph stored in seperate div within the main div
                                        html.Div([
                                            dcc.Graph(id='simulate_fig')
                                            ])
                                    ],className="five columns"),


                            # This chunk simulates the damages 
                            html.Div([
                                dcc.Graph(id='sim_dmg')
                            ],className="three columns")

                        ],className="pretty_container row",
                            style={
                                'backgroundColor' : "white"
                            })
                    ],style={"display": "flex", "flex-direction": "column"})


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#                                                   Callback Logic

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@app.callback([
    dash.dependencies.Output('cyclones_dropdown', 'options'),
    dash.dependencies.Output('line_fig', 'figure'),
    dash.dependencies.Output('slider-output-container', 'children'),
    dash.dependencies.Output('total_in_year_string', 'children'),
    dash.dependencies.Output('total_in_year_count', 'children'),
    dash.dependencies.Output('catone', 'children'),
    dash.dependencies.Output('cattwo', 'children'),
    dash.dependencies.Output('catthree', 'children'),
    dash.dependencies.Output('catfour', 'children'),
    dash.dependencies.Output('catfive', 'children'),
    dash.dependencies.Output('all_cyclones', 'children')],
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('cat_dropdown', 'value')
    ])
def reset_cyclone_options(year,cat):
    new = historical_dmg_df_dict[year]
    output = {}
    for i in new:
        if i[2] == cat:
            output[i[0]] = [i[0],i[1]]
    value = year
    viz_df = line_df[line_df.SEASON.isin([value])]
    figure = px.line_mapbox(viz_df,hover_name= "NAME", lat="LAT", lon="LON", color="SID", zoom=2)
    figure.update_layout(mapbox_style="carto-darkmatter", mapbox_zoom=2, mapbox_center_lat = 30.5987,mapbox_center_lon = 134.269)

    children = 'You have selected "{}"'.format(value)

    random_dict = {'1':0,'2':0,'3':0,'4':0,'5':0}
    re_count_dict = {}
    for i in counting_dict:
        if counting_dict[i][0] not in re_count_dict:
            re_count_dict[counting_dict[i][0]] = random_dict.copy()
        if counting_dict[i][0] in re_count_dict:
            cat = counting_dict[i][1]
            re_count_dict[counting_dict[i][0]][str(cat)] += 1
            
    re_count_list = []
    for i in re_count_dict:
        tiny_list = []
        year = i
        tiny_list.append(year)
        for j in re_count_dict[i]:
            tiny_list.append(re_count_dict[i][j])
        re_count_list.append(tiny_list)
    for i in re_count_list:
        if i[0] == value:
            catone = i[1]
            cattwo = i[2]
            catthree = i[3]
            catfour = i[4]
            catfive = i[5]
    
    counts_per_year = year_count_df.values.tolist()
    disp = 0
    for i in counts_per_year:
        if i[0] == value:
            disp = i[1]

    year_str = "Total no. of Typhoons in " + str(value)
    year_cnt = disp
    all_cyclones = "Figure Shows Paths of Typhoons in " + str(value)

    return [{'label': i, 'value': output[i][1]} for i in output], figure , children , year_str , str(year_cnt) , str(catone), str(cattwo), str(catthree), str(catfour), str(catfive), all_cyclones







@app.callback(
    dash.dependencies.Output('cyclones_dropdown', 'value'),
    [dash.dependencies.Input('cyclones_dropdown', 'options')])
def set_cyclones_value(options):
    return options[0]['value']



@app.callback(
    dash.dependencies.Output('meteor', 'figure'),
    [dash.dependencies.Input('drop', 'value')])

def update_meteorological_data(value):
    temp = temp_df.copy()
    taverage_dict = {}
    divide_t = 0
    # insert code for changing the copy into one that only contains selected countries
    temp = temp.loc[temp['Country'].isin(value)]
    temp = temp[["Year","Average_Temperature"]]
    temp_list = temp.values.tolist()
    for i in temp_list:
        if i[0] == 2000:
            divide_t += 1
        if i[0] in taverage_dict:
            taverage_dict[i[0]] += i[1]
        else:
            taverage_dict[i[0]] = i[1]
    for i in taverage_dict:
        taverage_dict[i] = taverage_dict[i]/divide_t
    temperature_df = pd.DataFrame(list(taverage_dict.items()),columns = ['Year','Temperature']) 

    precep = precep_df.copy()
    paverage_dict = {}
    divide_p = 0
    # insert code for changing the copy into one that only contains selected countries
    precep = precep.loc[precep['Country'].isin(value)]
    precep = precep[["Year","Average_Precipitation"]]
    precep_list = precep.values.tolist()
    for i in precep_list:
        if i[0] == 2000:
            divide_p += 1
        if i[0] in paverage_dict:
            paverage_dict[i[0]] += float(i[1].replace(',', ''))
        else:
            paverage_dict[i[0]] = float(i[1].replace(',', ''))
    for i in paverage_dict:
        paverage_dict[i] = paverage_dict[i]/divide_p
    precipitation_df = pd.DataFrame(list(paverage_dict.items()),columns = ['Year','Precipitation']) 



    # Create figure with secondary y-axis
    mfig = go.Figure()

    # Add traces
    mfig.add_trace(
        go.Scatter(x=year_count_df['Year'],y=year_count_df['Number of Cyclones'],line={'color':"#636EFA", "width":3}, name="Number of Typhoons per Year"))

    mfig.add_trace(
        go.Scatter(x=temperature_df['Year'],y=temperature_df['Temperature'], name="Average Temperature", 
                line=dict(color='#00CC96', width=4),yaxis="y2"))

    mfig.add_trace(
        go.Scatter(x=precipitation_df['Year'],y=precipitation_df['Precipitation'], name="Average Precipitation",
                line=dict(color='#EF553B', width=4),yaxis="y3"))



    # Add figure title
    mfig.update_layout(
        xaxis=dict(domain=[0.1, 0.9]
        ),
        yaxis=dict(
            title="<b>Number Of Typhoons<b>",
            titlefont=dict(
            color="#636EFA",size=18
            ),tickfont=dict(
            color="#636EFA")
        ),
        yaxis2=dict(
            title="<b>Temperature<b> (Degree Celcius)",
            titlefont=dict(
            color="#00CC96",size=18
            ),tickfont=dict(
            color="#00CC96"),
            anchor="free",
            overlaying="y",
            side="left",
            position=0
        ),
        yaxis3=dict(
            title="<b>Preipitation<b> (mm)",
            titlefont=dict(
            color="#EF553B",size=18
            ),tickfont=dict(
            color="#EF553B"),
            anchor="x",
            overlaying="y",
            side="right",
        
    ))
    return mfig


@app.callback(
    [dash.dependencies.Output('single_line_fig', 'figure'),dash.dependencies.Output('selected_cyclone', 'children'),dash.dependencies.Output('dmg_for_cyclone', 'children')],
    [dash.dependencies.Input('cyclones_dropdown', 'value')])

def set_figure(value):
    single_df = line_df[line_df.SID.isin([value])]
    figure = px.line_mapbox(single_df,hover_name= "NAME", lat="LAT", lon="LON", color="SID", zoom=2)
    figure.update_layout(mapbox_style="carto-darkmatter", mapbox_zoom=2, mapbox_center_lat = 30.5987,mapbox_center_lon = 134.269)
    name = single_df['NAME'].iloc[0]
    selected_cyclone = "Simulated Path of Typhoon "+name

    dmg_for_cyclone = "Damage caused by Typhoon "+name

    return figure , selected_cyclone, dmg_for_cyclone

@app.callback(
    dash.dependencies.Output('dmg', 'figure'),
    [dash.dependencies.Input('cyclones_dropdown', 'value')])
def calculate_damage(value):
    #gathers the values of unique prefectures with highest cat
    sid_df = line_df[line_df.SID.isin([value])]
    sid_df = sid_df[sid_df.COUNTRY.isin(['JP'])]
    sid_df = sid_df[["PREF","CATEGORY"]]
    sid_list = sid_df.values.tolist()
    unique_dict = {}
    sid_list
    for i in sid_list:
        prefecture = i[0]
        cat = i[1]
        if prefecture not in unique_dict:
            unique_dict[prefecture] = i[1]   
        for j in unique_dict:
            if j == i[0]:
                old = unique_dict[j]
                new = i[1]
                if new>old:
                    unique_dict[j] = new
    damage_value = 0
    for i in unique_dict:
        if i in pv_dict:
            val = pv_dict[i]
            cat = damages_dict[str(unique_dict[i])]
            total = val*cat
            damage_value += total
        elif i == "Hyogo":
            val = pv_dict['Hyōgo']
            cat = damages_dict[str(unique_dict[i])]
            total = val*cat
            damage_value += total
        elif i == "Nagasaki":
            val = pv_dict['Naoasaki']
            cat = damages_dict[str(unique_dict[i])]
            total = val*cat
            damage_value += total
        elif i == "Saga Prefecture":
            val = pv_dict['Saga']
            cat = damages_dict[str(unique_dict[i])]
            total = val*cat
            damage_value += total
    fig = fig = go.Figure(go.Indicator(
    mode = "number",
    value = damage_value,
    number = {'prefix': "$"},
    domain = {'x': [0, 1], 'y': [0, 1]}))

    return fig






# Code required for the selection of coordinates
@app.callback(Output(MARKER_GROUP_ID, 'children'), [Input(MAP_ID, 'click_lat_lng')])
def set_marker(x):
    if not x:
        return None
    return dl.Marker(position=x, children=[dl.Tooltip('Test')])


@app.callback([Output(COORDINATE_CLICK_ID, 'children'),Output('cor_table', 'figure'),dash.dependencies.Output('simulate_fig', 'figure')], [Input(MAP_ID, 'click_lat_lng')])
def click_coord(e):
    if not e:
        coords = ["",""]
        # cor = {'Lat':[],'Lon':[]}
        cor["Lat"].append(coords[0])
        cor["Lon"].append(coords[1])
    else:
        coords = json.dumps(e)
        cor["Lat"].append(e[0])
        cor["Lon"].append(e[1])
    
    #turn cor into a df
    cor_df = pd.DataFrame.from_dict(cor)
    # Showing selected coordinates in table form
    cord_table = go.Figure(data=[go.Table(
        header=dict(values=list(cor_df.columns)[0:2],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cor_df.Lat[2::], cor_df.Lon[2::]],
                fill_color='lavender',
                align='left'))
    ])

    cord_table.update_layout(
    title_text="Your Selected Coordinates"
    )

    sim_df = cor_df[2::]


    if len(cor["Lat"]) < 3:
        figure = go.Figure(go.Indicator(
        mode = "number",
        value = 0,
        number = {'font': {"color":'snow'}},
        title = {"text": "Select Coordinates on the Map above to Begin"},
        domain = {'x': [0, 1], 'y': [0, 1]}))
        figure.update_layout(paper_bgcolor = "snow")
    else:
        figure = px.line_mapbox(sim_df, lat="Lat", lon="Lon", zoom=2)
        figure.update_layout(mapbox_style="carto-darkmatter", mapbox_zoom=2, mapbox_center_lat = 36.73008022131222,mapbox_center_lon = 139.57030949592613)

    return coords , cord_table , figure
    

@app.callback([Output('cor_table', 'figure'),dash.dependencies.Output('simulate_fig', 'figure'),Output('sim_dmg', 'figure')],
              [Input('btn-nclicks-1', 'n_clicks'),
               Input('btn-nclicks-2', 'n_clicks')])
def displayClick(btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # deletes last item
    if 'btn-nclicks-1' in changed_id:
        del cor["Lat"][-1]
        del cor["Lon"][-1]
    #turn cor into a df
        cor_df = pd.DataFrame.from_dict(cor)
    # Showing selected coordinates in table form
        cord_table = go.Figure(data=[go.Table(
            header=dict(values=list(cor_df.columns)[0:2],
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[cor_df.Lat[2::], cor_df.Lon[2::]],
                    fill_color='lavender',
                    align='left'))
        ])

    # deletes everything
    elif 'btn-nclicks-2' in changed_id:
        cor["Lat"] = ["",""]
        cor["Lon"] = ["",""]
    #turn cor into a df
    cor_df = pd.DataFrame.from_dict(cor)
# Showing selected coordinates in table form
    cord_table = go.Figure(data=[go.Table(
        header=dict(values=list(cor_df.columns)[0:2],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cor_df.Lat[2::], cor_df.Lon[2::]],
                fill_color='lavender',
                align='left'))
    ])
    sim_df = cor_df[2::]


    if len(cor["Lat"]) < 3:
        figure = go.Figure(go.Indicator(
        mode = "number",
        value = 0,
        number = {'font': {"color":'snow'}},
        title = {"text": "Select Coordinates on the Map above to Begin"},
        domain = {'x': [0, 1], 'y': [0, 1]}))
        figure.update_layout(paper_bgcolor = "snow")
    else:
        figure = px.line_mapbox(sim_df, lat="Lat", lon="Lon", zoom=2)
        figure.update_layout(mapbox_style="carto-darkmatter", mapbox_zoom=2, mapbox_center_lat = 36.73008022131222,mapbox_center_lon = 139.57030949592613)


    fig = go.Figure(go.Indicator(
                        mode = "number",
                        value = 0,
                        number = {'prefix': "$"},
                        domain = {'x': [0, 1], 'y': [0, 1]}))

    return cord_table , figure , fig

@app.callback(Output('sim_dmg', 'figure'),
              [Input('btn-nclicks-3', 'n_clicks'),Input('sim_cat_dropdown', 'value')])

def generate_value(btn3,cat):
    
    cor_df = pd.DataFrame.from_dict(cor)
    cor_df = cor_df[2::]

    cord_list = cor_df.values.tolist()
    litt = []
    for lists in cord_list:
        lat = lists[0]
        lon = lists[1]

        response = requests.get("https://api.bigdatacloud.net/data/reverse-geocode-client?", params={"Latitude":lat,"Longitude":lon,"localityLanguage":"en"})
        response = response.json()
        j_response = response['localityInfo']['administrative']
        counter = 0
        if response["principalSubdivision"] == "Saga Prefecture":
            counter += 1
            litt.append("Saga")
        if j_response:
            for i in j_response:
                for j in i:
                    if j == 'adminLevel' and i[j] == 4 and counter == 0 :
                        if 'isoName' in i:
                            val = (i['isoName'])
                            if val is not None:
                                counter +=1
                                litt.append(val)

    # removes duplicated prefractures
    litt = list(dict.fromkeys(litt))


    damage_value = 0
    category_gen = cat

    for i in litt:
        if i in pv_dict:
            val = pv_dict[i]
            cat = damages_dict[str(category_gen)]
            total = val*cat
            damage_value += total
        elif i == "Hyogo":
            val = pv_dict['Hyōgo']
            cat = damages_dict[str(category_gen)]
            total = val*cat
            damage_value += total
        elif i == "Nagasaki":
            val = pv_dict['Naoasaki']
            cat = damages_dict[str(category_gen)]
            total = val*cat
            damage_value += total
        elif i == "Saga Prefecture":
            val = pv_dict['Saga']
            cat = damages_dict[str(category_gen)]
            total = val*cat
            damage_value += total
    
    fig = fig = go.Figure(go.Indicator(
    mode = "number",
    value = damage_value,
    number = {'prefix': "$"},
    domain = {'x': [0, 1], 'y': [0, 1]}))

    return fig

@app.callback(dash.dependencies.Output('korro_fig', 'figure'),
              [dash.dependencies.Input('korro_year-dropdown', 'value')])
def Click(year):

    value = year
    Country_value = "JP"
    dounting_dict_for_year = {}
    pre = origindf.copy()
    pre = pre[["Prefrecture"]]
    pre["count"] = 0
    pre["Weighted_count"] = 0
    final_list = pre.values.tolist()
    uni_df = jcpc_origin.copy()
    uni_df = uni_df[uni_df.SEASON.isin([value])]
    uni_df =uni_df[uni_df.COUNTRY.isin([Country_value])]
    uni_list = uni_df[["SID","PREF","CATEGORY"]].values.tolist()
    for i in uni_list:
        if i[0] not in dounting_dict_for_year:
            dounting_dict_for_year[i[0]] = {}
        for sid in dounting_dict_for_year:
            if sid == i[0]:
                if i[1] not in dounting_dict_for_year[i[0]]:
                    dounting_dict_for_year[i[0]][i[1]] = i[2]
            for prefecture in dounting_dict_for_year[sid]:
                old = dounting_dict_for_year[sid][prefecture]
                new = i[2]
                if new > old:
                    dounting_dict_for_year[sid][prefecture] = new

    for pref_list in final_list:
        for sid in dounting_dict_for_year:
            for prefecture in dounting_dict_for_year[sid]:
                if pref_list[0] == prefecture:
                    pref_list[1] += 1
                    pref_list[2] += dounting_dict_for_year[sid][prefecture]
                
                elif prefecture == "Hyogo" and pref_list[0] == 'Hyōgo':
                    pref_list[1] += 1
                    pref_list[2] += dounting_dict_for_year[sid][prefecture]
                
                elif prefecture == "Nagasaki" and pref_list[0] == 'Naoasaki':
                    pref_list[1] += 1
                    pref_list[2] += dounting_dict_for_year[sid][prefecture]
                
                elif prefecture == "Saga Prefecture" and pref_list[0] == 'Saga':
                    pref_list[1] += 1
                    pref_list[2] += dounting_dict_for_year[sid][prefecture]

    final_df = DataFrame (final_list,columns=['Prefecture','Count','Weighted Count'])
    #Using the populated library, input a new column called 'id'
    final_df['id'] = final_df['Prefecture'].apply(lambda x: prefec_id[x])

    # Create the map
    korro_fig=px.choropleth_mapbox(final_df,
                        locations="id",
                        geojson=data,
                        color="Count",
                        hover_name= "Prefecture",
                        mapbox_style='carto-darkmatter',
                        center={'lat':36.73008022131222,'lon':139.57030949592613},
                        color_continuous_scale=px.colors.diverging.Portland,
                        zoom = 3
                        )
    korro_fig.update_layout(clickmode='event+select')
    korro_fig.update_layout(
    title_text="Number of times each Prefecture experienced a Typhoons in "+str(value), title_x=0.5
    )

    return korro_fig

@app.callback(
    Output('click-data', 'figure'),
    Input('korro_fig', 'clickData'))
def display_click_data(clickData):
    dic = clickData
    prefrecture = dic["points"][0]["hovertext"]
    final_df = jcpc_origin.copy()
    year_dic = {}
    test = prefrecture
    if test == "Hyōgo":
        pref = "Hyogo"
    elif test == "Naoasaki":
        pref = "Nagasaki"
    elif test == "Saga":
        pref = "Saga Prefecture"
    else:
        pref = test
    final_df = final_df[final_df.PREF.isin([pref])]
    final_df =final_df[final_df.COUNTRY.isin(["JP"])]
    final_df = final_df.drop_duplicates(subset='SID', keep="first")
    final_df = final_df[["SEASON"]]
    final_list = final_df.values.tolist()
    for i in final_list:
        if i[0] not in year_dic:
            year_dic[i[0]] = 1
        else:
            year_dic[i[0]] += 1
    finished_list = []
    for each in year_dic:
        finished_list.append([each,year_dic[each]])


    finished_df = DataFrame (finished_list,columns=['year','count'])
    fig = px.bar(finished_df, x='year', y='count')
    fig.update_layout(
    title_text="Number of Typhoons that hit "+prefrecture+" from 2000 ~ 2020", title_x=0.5
    )
    return fig


app.run_server(debug=False, use_reloader=True)  # Turn off reloader if inside Jupyter