import requests
import json
import pandas as pd
from dash import Dash, dash_table, html, callback, Output, Input, no_update, State
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


def get_city_id():

    df = pd.read_csv('data/city_id.csv')
    df.columns = ["country","city","code"]

    return df

def get_weather_forecase(City_ID):

    url = "http://worldweather.wmo.int/kr/json/"+ City_ID +"_kr.xml"
    response = requests.get(url)
    content = response.text
    jsonStr = json.loads(content)
    
    city = jsonStr['city']['cityName']
    country = jsonStr['city']['member']['memName']
    region_text = city + " " + country
    try:
        df_month = pd.DataFrame(jsonStr['city']['climate']['climateMonth'])
        col_month = ['month','minTemp','maxTemp','raindays']
        df_month = df_month[col_month]
    except:
        df_month = pd.DataFrame([{"month":'No Data',"minTemp":0,"maxTemp":0,"raindays":0},])

    
    try:
        df_forecast = pd.DataFrame(jsonStr['city']['forecast']['forecastDay'])
        col_forecast = ['forecastDate','minTemp','maxTemp','weather']
        df_forecast = df_forecast[col_forecast]
    except:
        df_forecast = pd.DataFrame([{"forecastDate":'No Data',"minTemp":0,"maxTemp":0,"weather":0},])

    return region_text, df_month, df_forecast


df_city_info = get_city_id()
list_country = df_city_info['country'].unique()


app = Dash(__name__)
app.title = "Weather Forecast"
server = app.server


dropdown_Country = html.Div(
    [
        dbc.Label("Select Country"),
        dcc.Dropdown(
            id = "select-country",
            options = [
                {"label": country, "value": country} 
                for country in list_country]
            )
    ]
)

dropdown_City = html.Div(
    [
        dbc.Label("Select City"),
        dcc.Dropdown(
            id = "select-city")
    ]
)

datatable_forecast = html.Div(
    [
        dbc.Container(
            html.I(
                id = 'forecast-table-title', 
            ),className='card-header',style={"background":"#E0B787"}),

        html.Div(
            [
                dash_table.DataTable(
                    id = 'weather-table',
                    style_table={'overflowX': 'auto'}
                )
            ],className="card-body",style={"background":'#F3F2DC'}
        ),
    ],className='card mb-4'
)

datatable_month = html.Div(
    [
        dbc.Container(
            html.I(
                id = 'month-table-title', 
            ),className='card-header',style={"background":"#E0B787"}),

        html.Div(
            [
                dash_table.DataTable(
                    id = 'month-table',
                    style_table={'overflowX': 'auto'}
                )
            ],className="card-body",style={"background":'#F3F2DC'}
        ),
    ],className='card mb-4'
)

app.layout = dbc.Container(
    [
        html.Hr(),
        dbc.Container(
            [
                dropdown_Country,
                dropdown_City,
                datatable_forecast,
                datatable_month,
            ],className="container-fluid px-4"
            ),
    ],
)

@callback(
    Output("select-city",'options'),
    [Input("select-country",'value')],
)
def update_gu(country):
    return [{"label": city, "value": city} for city in df_city_info[df_city_info['country']==country].city.unique()]


@callback(
    [Output("weather-table",'columns'),
     Output("weather-table",'data'),
     Output("month-table",'columns'),
     Output("month-table",'data')],
    [Input("select-city",'value')],
    [State("select-country",'value')]
)
def update_gu(city,country):

    if city is None:
        return no_update

    mask = (
            (df_city_info.country == country)
            & (df_city_info.city == city)
        )
    
    city_code = str(df_city_info[mask].iat[0,2])
    print(city_code)

    region_text, df_month, df_forecast = get_weather_forecase(city_code)


    forecast_cols = [
        {"name": i, "id": i} for i in df_forecast.columns
    ]
    forecast_data = df_forecast.to_dict('records')

    month_cols = [
        {"name": i, "id": i} for i in df_month.columns
    ]
    month_data = df_month.to_dict('records')


    return forecast_cols,forecast_data,month_cols,month_data


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0',port=8100)