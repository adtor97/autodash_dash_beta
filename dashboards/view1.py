import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from flask import request, session
from utils import utils
import os
import bcrypt

def serve_layout():

    layout = html.Div(
                        [
                        dbc.Row(
                                    [
                                        html.H1(
                                                "View 1"
                                                , id="title-view1"
                                                , className="title"
                                                )
                                    ]
                                    , justify = 'center'
                                    , style={"margin-top":"2%", "margin-bottom":"5%"}
                                )
                        ]
                    )

    return layout

def init_callbacks(dash_app):

    #@dash_app.callback(
    #Output('element2', 'attribute'),
    #Input('element1', 'attribute'),
    #prevent_initial_call = True
    #)
    #def function1(element1_attribute):
        #var = 1
        #return var

    return None
