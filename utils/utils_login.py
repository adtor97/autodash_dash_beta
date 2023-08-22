import bcrypt, os, json
import pandas as pd
from utils import utils_google

gs_name = "base_dash_model"
gs_sheet_name = "users"


def loginizer(username, password):
    #print(password)
    password = str.encode(str(password))
    #print(password)
    username = username.lower()

    df_user = utils_google.read_ws_data(utils_google.open_ws(gs_name, gs_sheet_name))
    df_user = df_user[(~df_user["userPassword"].isnull())
                    & (~df_user["userPassword"].isna())
                    & (df_user["userPassword"] != "")
                    & (df_user["userEmail"] == username)
                    ]
    #print(df_user)

    df_user["matching"] = df_user.apply(lambda x: True if bcrypt.checkpw(password, str.encode(str(x['userPassword']))) else False, axis = 1)
    df_user = df_user[(df_user["matching"]==True)]
    #print(df_user)
    if len(df_user)==0: return False
    df_user.drop(columns=["userPassword", "matching"], inplace=True)
    views = df_user.views.values[0]
    df_user = df_user.to_json(date_format='iso', orient='records')
    user = json.loads(df_user)[0]
    print("user", user)
    return user
