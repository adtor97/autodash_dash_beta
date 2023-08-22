from dashboards import login, view1
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
from flask import request, session, redirect, render_template
from datetime import datetime, date
import os
from waitress import serve

def create_dashboard():
    template_dash = open("templates/layout.html")
    # print(template_dash.read())
    template_dash_ = str(template_dash.read()).replace('\n','')
    # print
    layout = str(template_dash_)

    """Create a Plotly Dash dashboard."""
    app = dash.Dash(__name__,
                    external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css','https://unpkg.com/dash.nprogress@latest/dist/dash.nprogress.js',],
                    meta_tags = [{"name": "viewport", "content": "width=device-width"}],
                    index_string=layout
                    )
                    # Create Layout

    app.title = "NAME OF WEB"
    #auth = dash_auth.BasicAuth(
    #                            app,
    #                            VALID_USERNAME_PASSWORD_PAIRS
    #                            )
    return app

app = create_dashboard()
app.config['suppress_callback_exceptions'] = True
server = app.server
server.secret_key = str(date.today())+"23"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False)
    , html.Div(id='page-content')
    , dcc.Store(id='user')
])

index_layout = html.Div(
                            [
                                html.Div(
                                        id='none'
                                        , children=[]
                                        , style={'display': 'none'}
                                        )
                                , html.Div(
                                        dcc.Store(
                                                id='user-info'
                                                )
                                        )
                                , dbc.Row(
                                        [
                                            html.H1(
                                                    "Choose your View"
                                                    , id="title"
                                                    )
                                        ]
                                        , justify = 'center'
                                        , style={"margin-top":"2%", "margin-bottom":"2%"}
                                        )
                                , dbc.Row(
                                        id="home-row-link"
                                        , style={"min-width":"25%", 'display':'flex'}
                                        )
                            ]
                            , style={"margin-bottom":"100px", "max-width":"80%", 'margin-left':'auto', 'margin-right':'auto'}
                        )

login_layout = login.serve_layout()
login.init_callbacks(app)

view1_layout = view1.serve_layout()
view1.init_callbacks(app)

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    print("display_page")

    if pathname.lower() == '/login':
        try:  session.pop("user")
        except: pass
        return login_layout

    if 'password' in pathname.lower():
        try:  session.pop("user")
        except: pass
        return password_layout

    try:
        user = session["user"]
    except:
        return login_layout

    if pathname.lower() == '/':
        app.title = "Home"
        return index_layout
    if pathname.lower() == '/view1' and 'view1' in user["views"]:
        app.title = "View1"
        return view1_layout
    else:
        return dcc.Location(id='redirect-home', href='/', refresh=True)
        #return index_layout
    # You could also return a 404 "URL not found" page here

@app.callback(dash.dependencies.Output("home-row-link", 'children'),
              [dash.dependencies.Input('none', 'children')])
def display_links(none):
    user = session["user"]
    print("user", user, type(user))
    views = [{"name":"View 1", "path":"view1", "description":"View hola mundo"},
            ]
    def link_format(name, path, description):
        path = f"/{path}"
        link = dbc.Col([dcc.Link(
                                name
                                , href=path
                                , refresh=True
                                , id=f"home-link-{path}"
                                , className="home-link")
                        , dbc.Tooltip(
                                description
                                , target = f"home-link-{path}"
                                )
                        ]
                , className="home-col-link"
                , sm="12"
                , md="6"
                , lg="4")
        return link
    print("views", views, type(views))
    print("views[0]", views[0], type(views[0]))
    links = [link_format(view["name"], view["path"], view["description"]) for view in views if view["path"] in user["views"]]
    links = list(links)
    return links

@app.callback(
    Output({'type': 'home-link-description', 'index': MATCH}, 'style'),
    Input({'type': 'home-link', 'index': MATCH}, 'hoverData'),
    prevent_initial_callback=True
    )
def display_links_description(hoverData):
    print("display_links_description")
    print(hoverData)
    if hoverData is None: return {"display":"none"}
    else: return None

if __name__ == '__main__':
    serve(server, host="0.0.0.0", port=8050)
    #serve(server, host="127.0.0.1", port=8050)
    #app.run_server(debug=False)
