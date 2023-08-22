import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from flask import request, session
from utils import utils
import os
import bcrypt
import geopandas as gpd
import plotly.express as px
from math import sqrt
from utils.utils_geo import *


def serve_layout():

    layout = html.Div(
                        [
                        dbc.Row(
                                    [
                                        html.H1(
                                                "Static Pre Covid App Copy"
                                                , id="title-view1"
                                                , className="title"
                                                )
                                    ]
                                    , justify = 'center'
                                    , style={"margin-top":"2%", "margin-bottom":"5%"}
                                )
                        , dbc.Row(
                                    [
                                        html.P(
                                                f"Static app, filters in progress. All districts, Asc for {list(ind_labels.keys())[0]} and {list(ind_labels.keys())[4]}"
                                                )
                                    ]
                                    , justify = 'center'
                                )
                        , dbc.Row(
                                    [
                                        dbc.Col(
                                                    [
                                                        html.H5("Select district")
                                                        , utils.dropdown(
                                                                                id="view1-dropdown-district"
                                                                                , options=[]
                                                                                , value=None
                                                                                , placeholder="Select district"
                                                                                , multi=False
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select # areas")
                                                        , dcc.Slider(
                                                                                id="view1-slider-areas",
                                                                                min=0,
                                                                                max=100
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select coverage (meters)")
                                                        , dcc.Slider(
                                                                                id="view1-slider-coverage",
                                                                                min=0,
                                                                                max=10000
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select main var")
                                                        , utils.dropdown(
                                                                                id="view1-dropdown-main_var"
                                                                                , options=[]
                                                                                , value=None
                                                                                , placeholder="Select main var"
                                                                                , multi=False
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select order for main var")
                                                        , utils.dropdown(
                                                                                id="view1-dropdown-order_main_var"
                                                                                , options=[]
                                                                                , value=None
                                                                                , placeholder="Select order main var"
                                                                                , multi=False
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select second var")
                                                        , utils.dropdown(
                                                                                id="view1-dropdown-second_var"
                                                                                , options=[]
                                                                                , value=None
                                                                                , placeholder="Select second var"
                                                                                , multi=False
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )
                                        , dbc.Col(
                                                    [
                                                        html.H5("Select order for second var")
                                                        , utils.dropdown(
                                                                                id="view1-dropdown-order_second_var"
                                                                                , options=[]
                                                                                , value=None
                                                                                , placeholder="Select order second var"
                                                                                , multi=False
                                                                            )
                                                    ]
                                                    , lg=4
                                                    , md=6
                                                    , sm=12
                                                )

                                    ]
                                )
                        , dbc.Row(
                                    id='view1-row-first'
                                )
                        ]
                    )

    return layout

def init_callbacks(dash_app):

    @dash_app.callback(
    Output('view1-row-first', 'children'),
    Input('title-view1', 'children'),
    prevent_initial_call = False
    )
    def show_graph(title):

        print()
        print('-'*30)

        # Read data
        def read_gpd(file):
            return gpd.read_file(file)

        hexs = read_gpd('assets/inputs/lima_hexs9_complete.geojson')
        candidate_green_areas = read_gpd('assets/inputs/candidate_green_areas.geojson')
        lima_distritos = read_gpd('assets/inputs/lima_distritos.geojson')

        # Filtra el distrito WORK IN PROGRESS
        district_opts = ['Todos'] + sorted(lima_distritos['distrito'].unique().tolist())
        district = "Todos"

        # Filter datasets within selected district
        if district == 'Todos':
            selected_district = lima_distritos
            selected_hexs = hexs
            selected_green_areas = candidate_green_areas
            zoom_level = 9
            hexring_range_dist = 2
            radius_max = 10000
            radius_step = 100
            lat = -12.0630149
            lon = -77.0296179
        else:
            selected_district = lima_distritos.query(f"distrito == '{district}'")
            selected_hexs = gpd.clip(hexs, selected_district)
            selected_green_areas = gpd.clip(candidate_green_areas, selected_district)
            # WARNING: There could be no green areas within the selected district
            zoom_level = 12
            selected_district_poly = selected_district.to_crs(epsg=32718).geometry.iloc[0]
            hexring_range_dist = calc_range_distances(selected_district_poly)
            radius_max = int(sqrt(selected_district_poly.area) * 0.10)
            radius_step = int(radius_max / 20)
            lat = selected_district.lat.iloc[0]
            lon = selected_district.lon.iloc[0]
        print('hexs shape:', selected_hexs.shape)
        print('green areas shape:', selected_green_areas.shape)

        n_candidates = 20
        radius = (radius_max+radius_step)/2

        prim_ind = list(ind_labels.keys())[0] # preselect ingr_per, Ai 4
        prim_ind_sort = 'Ascendentemente' # preselect ascending=False, True

        threshold_min = selected_hexs[ind_labels[prim_ind]].min()
        threshold_max = selected_hexs[ind_labels[prim_ind]].max()
        threshold_value = selected_hexs[ind_labels[prim_ind]].median()

        if threshold_min >= threshold_max:
            # Handle boleean vars
            threshold = 0
            # prim_ind_sort = 'Descendentemente' # TODO: Find a better way to handle this
        else:
            if sort_ascending[prim_ind_sort]:
                threshold_type = 'máximo'
            else:
                threshold_type = 'mínimo'
            threshold = (threshold_min+threshold_max)/2

        # TODO: Delete active primary indicator from this second indicator selectbox
        second_ind = list(ind_labels.keys())[4] # preselect population_2020
        second_ind_sort = 'Ascendentemente'  # preselect ascending=False

        # Data processing
        primary_ind = create_ind_param(prim_ind, prim_ind_sort)
        secondary_ind = create_ind_param(second_ind, second_ind_sort)

        zones_df, filtered_green_areas = calc_candidates(selected_hexs, n_candidates, radius, threshold,
                                                         primary_ind,
                                                         secondary_ind,
                                                         selected_green_areas,
                                                         hexring_range_dist)
        indicators_ok = False
        if filtered_green_areas.shape[0] > 0:
            n_per_zone = 10 # Could be choosen by the user

            rselected_green_areas = sample_random_candidates(filtered_green_areas, 'zone_id', n_per_zone) # random selection

            topN_green_areas = (filtered_green_areas.sort_values([primary_ind['col_name'], secondary_ind['col_name']],
                                    ascending=[primary_ind['ascending'], secondary_ind['ascending']])
                                    .groupby('zone_id').head(n_per_zone)) # select top N green areas

            sel_inds = ['population_2020', 'Retail', 'Ai', 'INGR_PER', 'vulnerabilidad_hidrica'] # Could be choosen by the user
            groups = {f'Top {n_per_zone}': topN_green_areas,
                    'Aleatorio': rselected_green_areas}

            try:
                inds = get_indicators(sel_inds, groups, filtered_green_areas)
                indicators_ok = True
                print(inds)
            except ValueError:
                pass


        # Create plots
        fig = px.choropleth_mapbox(zones_df,
                                   geojson=zones_df.geometry,
                                   locations=zones_df.index,
                                   color=["1"]*zones_df.shape[0],
                                   opacity=0.25)

        fig.add_choroplethmapbox(geojson=selected_district.geometry.__geo_interface__,
                                 locations=selected_district.index,
                                 name='Distritos',
                                 customdata=selected_district['distrito'],
                                 z=["1"]*candidate_green_areas.shape[0],
                                 colorscale=[[0, 'rgba(255,255,255,0)'], [1,'rgba(255,255,255,0)']],
                                 marker_line_width=2,
                                 marker_line_color='rgba(0,0,0,0.2)',
                                 hovertemplate='Distrito:%{customdata}',
                                 hoverlabel_namelength = 0,
                                 showscale=False,)

        fig.add_choroplethmapbox(geojson=selected_green_areas.geometry.__geo_interface__,
                                 locations=selected_green_areas.index,
                                 name='Áreas Verdes',
                                 customdata=selected_green_areas['NOMBRE'],
                                 z=["1"]*selected_green_areas.shape[0],
                                 colorscale='greens',
                                 marker_line_color='rgba(0,255,0,0.2)',
                                 hovertemplate='Nombre:%{customdata}',
                                 hoverlabel_namelength = 0,
                                 showscale=False,)

        if indicators_ok:
            fig.add_choroplethmapbox(geojson=rselected_green_areas.geometry.__geo_interface__,
                                     locations=rselected_green_areas.index,
                                     customdata=rselected_green_areas['NOMBRE'],
                                     z=["1"]*rselected_green_areas.shape[0],
                                     colorscale='reds',
                                     marker_line_color='rgba(255,0,0,0.2)',
                                     hovertemplate='Nombre:%{customdata}',
                                     hoverlabel_namelength = 0,
                                     showscale=False,)

            fig.add_choroplethmapbox(geojson=topN_green_areas.geometry.__geo_interface__,
                                     locations=topN_green_areas.index,
                                     customdata=topN_green_areas['NOMBRE'],
                                     z=["1"]*topN_green_areas.shape[0],
                                     colorscale='blues',
                                     marker_line_color='rgba(0,0,255,0.2)',
                                     hovertemplate='Nombre:%{customdata}',
                                     hoverlabel_namelength = 0,
                                     showscale=False,)

        fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=zoom_level,
                          mapbox_center = {"lat": lat, "lon": lon},
                          showlegend=False, margin={"r":0,"t":0,"l":0,"b":0}, title="Zonas de interés seleccionadas")

        figs=[]
        figs.append(utils.format_fig(fig))
        if filtered_green_areas.shape[0] > 0 and indicators_ok:
            radar_fig = px.line_polar(inds, r='value_norm', theta='indicator_labels', color='group', line_close=True,
                                    hover_data={'value':':.2f', 'indicator':False, 'group':False, 'value_norm':False},
                                    labels=plotly_radar_labels, color_discrete_sequence=['blue', 'red'])
            radar_fig.update_layout(polar={'radialaxis': {'showticklabels': True}})
            figs.append(utils.format_fig(radar_fig))
        else:
            return('No tenemos registradas suficientes áreas verdes en estas zonas. Intenta cambiar los parámetros en la barra lateral de la izquierda para hayar nuevas zonas.')

        return figs
