import pandas as pd
import base64
from io import StringIO, BytesIO
from dash import html, dcc
from datetime import timedelta
import dash_bootstrap_components as dbc


def dropdown(id, options=[], value=[], multi=False, placeholder=""):
    dropdown = html.Div(
                        dcc.Dropdown(id=id,
                                    options=options,
                                    value=value,
                                    placeholder=placeholder,
                                    multi=multi)
                        )
    return dropdown

def list_to_where(thelist):
    thelist = str(thelist).replace('"',"'").replace("[","(").replace("]",")")
    #print(thelist)
    return thelist

months = {1:{"name":"January", "days":31, "number_text":"01", "short_name":"jan"},
	  2:{"name":"February", "days":[28, 29], "number_text":"02", "short_name":"feb"},
	  3:{"name":"March", "days":31, "number_text":"03", "short_name":"mar"},
	  4:{"name":"April", "days":30, "number_text":"04", "short_name":"apr"},
	  5:{"name":"May", "days":31, "number_text":"05", "short_name":"may"},
	  6:{"name":"June", "days":30, "number_text":"06", "short_name":"jun"},
	  7:{"name":"July", "days":31, "number_text":"07", "short_name":"jul"},
	  8:{"name":"August", "days":31, "number_text":"08", "short_name":"aug"},
	  9:{"name":"September", "days":30, "number_text":"09", "short_name":"sep"},
	  10:{"name":"October", "days":31, "number_text":"10", "short_name":"oct"},
	  11:{"name":"November", "days":30, "number_text":"11", "short_name":"nov"},
	  12:{"name":"December", "days":31, "number_text":"12", "short_name":"dec"}
	}

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    inputfilename = filename
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(BytesIO(decoded))
        return df
    except Exception as e:
        print(e)
        return None


def format_fig(fig):
    return dbc.Col(
                    dcc.Graph(
                                figure=fig
                            )
                    , width=12
                    , style={"padding":"5px"}
                    )
