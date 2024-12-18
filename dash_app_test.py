#Moscow code 294021
#Dubai code 323091
#запрос данных по api и создание json файла
# api_key = 'yI9Novx6WYEbkMGHp6D7rcjliPSrJTr0'
# forecast_hourly_api_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/'
# moscow_code = 294021
# dubai_code = 323091

# weather_info_moscow = requests.get(f'{forecast_hourly_api_url}{moscow_code}?apikey={api_key}&details=true&metric=true')
# weather_info_dubai = requests.get(f'{forecast_hourly_api_url}{dubai_code}?apikey={api_key}&details=true&metric=true')

# moscow_data = weather_info_moscow.json()
# dubai_data = weather_info_dubai.json()

# with open('moscow_forecast_24h.json', 'w') as file:
#     json.dump(moscow_data, file)

# with open('dubai_forecast_24h.json', 'w') as file:
#     json.dump(dubai_data, file)



import json
# import requests
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
with open('moscow_forecast_5days.json', 'r') as file:
    moscow_data = json.load(file)

with open('dubai_forecast_5days.json', 'r') as file:
    dubai_data = json.load(file)

app = Dash()

app.layout = [
        html.Div(id = 'cities_output',
                  children='Введите название городов:')
        ,
              html.Div(dcc.Input(id='city_1_input',
                  placeholder='1 город',
                  type = 'text',
                  value = ''
              )),
              html.Div(
                  dcc.Input(id = 'city_2_input',
                  placeholder='2 город',
                  type = 'text',
                  value = ''
              )),
              html.Div(html.Button('Отправить', id = 'submit_cities', n_clicks=0))]

@callback(
    Output(component_id='cities_output',
           component_property='children'),
    Input(component_id='submit_cities',
          component_property='n_clicks'),
    [State(component_id='city_1_input', 
           component_property='value'),
    State(component_id='city_2_input',
          component_property='value')],
    prevent_initial_call = True
)

def print_cities(n_clicks, city_1, city_2):
    return f'Первый город: {city_1}, Второй город: {city_2}'

if __name__ == '__main__':
    app.run(debug=True)