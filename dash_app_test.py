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
import pandas as pd
import plotly.express as px

api_key = 'qV7vDxXTitSMqoxec5n77w5D5txhR7Kk'
key_by_city_api_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'

class WeatherConditionManager:
    def __init__(self, api_key, key_by_city_api_url):
        self.api_key = api_key
        self.key_by_city_api_url = key_by_city_api_url

    def get_location_key_by_city(self, city):
        city = city.lower()
        try:
            return 'code'
            # city_info = requests.get(f"{self.city_info_api_url}?apikey={self.api_key}&q={city}", params = 'Key')
            # if city_info.status_code == 200:
            #     if city_info.json() == []:
            #         return 'wrong_city_error'
            #     city_data = city_info.json()

            #     location_key = city_data[0]['Key']
            #     return location_key
            # else:
            #     return city_info.status_code

        except:
            return 'error'
        
    def get_weather_info_1day(self, city):
        city = city.lower()
        forecast_api_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/'
        try:
            location_key = self.get_location_key_by_city(city)
            # if (location_key in [400, 401, 403, 404, 500, 503] or 
            #     location_key == 'wrong_city_error'):  
            #     return location_key        
            # weather_info = requests.get(f'{forecast_api_url}{location_key}?apikey={self.api_key}&details=true&metric=true')
            
            # if weather_info.status_code == 200:
            #     weather_data = weather_info.json()
            with open(f'C:/Users/Niko/Desktop/python_contest/Python_project_3/{city}_forecast_5days.json', 'r') as file:
                weather_data = json.load(file)


            minimal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
            maximal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
            humidity_day_minimum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Minimum"]
            humidity_day_maximum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Maximum"]
            wind_day_speed = weather_data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
            rain_day_probability = weather_data["DailyForecasts"][0]["Day"]["RainProbability"]
            snow_day_probability = weather_data["DailyForecasts"][0]["Day"]["SnowProbability"]
            ice_day_probability = weather_data["DailyForecasts"][0]["Day"]["IceProbability"]
            uv_index = weather_data["DailyForecasts"][0]['AirAndPollen'][5]["Value"]

            weather_info_list = [{'minimal_temp': minimal_temp, 
                                'maximal_temp' : maximal_temp, 
                                'humidity_day_minimum' : humidity_day_minimum, 
                                'humidity_day_maximum' : humidity_day_maximum, 
                                'wind_day_speed' : wind_day_speed, 
                                'rain_day_probability' : rain_day_probability, 
                                'snow_day_probability' : snow_day_probability,
                                'ice_day_probability' : ice_day_probability, 
                                'uv_index' : uv_index}]

            return weather_info_list
            
            # else:
            #     return weather_info.status_code

        except:
            return 'error'
        
    def create_dataframe(self, city):
        weather_info_list = self.get_weather_info_1day(city)

app = Dash()


app.layout = [
        html.Div(id = 'cities_output',
                  children='Введите название городов:'),
            html.Div(id = 'radio_items_description',
                     children='Выберите, на сколько дней вы хотите видеть прогноз погоды:'),
            html.Div(id = 'radio_items_container', 
                     children=[dcc.RadioItems(id = 'radio_items',
                         options=[{'label' : '1 день',
                                   'value' : '1_day'},
                                   {'label' : '3 дня',
                                   'value' : '3_day'},
                                   {'label' : '5 дней',
                                   'value' : '5_day'},],
                         value = '1_day'
                     )]),
              html.Div(dcc.Input(id='city_1_input',
                  placeholder='1 город',
                  type = 'text',
                  value = ''
              )),
            html.Div(id = 'dropdown_description_1',
                  children='Выберите интересующие метрики прогноза погода:'),
              html.Div(id = 'dropdown_container_1',
                       children = [dcc.Dropdown(id = 'city_1_dropdown',
                           options=['Температура', 'Влажность', 'Скорость ветра',
                                    'Вероятность осадков и льда', 'УФ-индекс'],
                                    value = 'Температура')]),
            html.Div(id = 'graph_container_1',children = [dcc.Graph(id='city_1_graph',
                  figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 1',
                'width' : 400,
                'height' : 400
            }}
              )]),
            html.Div(
                  dcc.Input(id = 'city_2_input',
                  placeholder='2 город',
                  type = 'text',
                  value = ''
              )),
            html.Div(id = 'dropdown_description_2',
                  children='Выберите интересующие метрики прогноза погода:'),
            html.Div(id = 'dropdown_container_2',
                       children = [dcc.Dropdown(id = 'city_2_dropdown',
                           options=['Температура', 'Влажность', 'Скорость ветра',
                                    'Вероятность осадков и льда', 'УФ-индекс'],
                                    value = 'Температура')]),
            html.Div(id = 'graph_container_2',children = [dcc.Graph(id='city_2_graph',
                  figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 2',
                'width' : 400,
                'height' : 400
            }}
              )]),
            html.Div(html.Button('Отправить', id = 'submit_cities', n_clicks=0))]

#callback, который обновляет первую строку на странице (информация о выбранных городах)

@app.callback(
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

#callback, отвечающий за отображение/скрытие графика для 1 города

@app.callback(Output(component_id='graph_container_1',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_graph_1(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие графика для 2 города
@app.callback(Output(component_id='graph_container_2',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_graph_2(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, который строит графики для 1 города
@app.callback(Output(component_id='city_1_graph',
                     component_property='figure'),
            [Input(component_id='submit_cities',
                  component_property='n_clicks'),
            Input(component_id='city_1_dropdown',
                  component_property='value'),
            Input(component_id='radio_items',
                  component_property='value')],
            State(component_id='city_1_input', 
           component_property='value'),
            prevent_initial_call = True)

def create_graphic_1(n_clicks, dropdown_value, radio_item_value, city_1):
    global api_key
    global key_by_city_api_url

    get_info = WeatherConditionManager(api_key, key_by_city_api_url)
    city_1_forecast = get_info.get_weather_info_1day(city_1)
    
    # создаём датафрейм с информацией о максимальной и минимальной температуре
    city_1_temp = [['minimal_temp', city_1_forecast[0]['minimal_temp']], 
                   ['maximal_temp', city_1_forecast[0]['maximal_temp']]]
    city_1_temp_df = pd.DataFrame(city_1_temp, 
                                columns=['temp', 'value'])
    
    # создаём и настраиваем фигуру для графика температуры
    city_1_temp_graph = px.bar(city_1_temp_df, x = 'temp', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_1_temp_df))
    city_1_temp_graph.update_layout(width = 400, height = 400,
                                    title = city_1)
    
    # создаём датафрейм с информацией о максимальной и минимальной влажности
    city_1_humidity = [['humidity_day_minimum', city_1_forecast[0]['humidity_day_minimum']], 
                    ['humidity_day_maximum', city_1_forecast[0]['humidity_day_maximum']]]
    city_1_humidity_df = pd.DataFrame(city_1_humidity, 
                                    columns=['humidity', 'value'])
    
    # создаём и настраиваем фигуру для графика влажности
    city_1_humidity_graph = px.bar(city_1_humidity_df, x = 'humidity', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_1_humidity_df))
    city_1_humidity_graph.update_layout(width = 400, height = 400, title = city_1)

    # создаём датафрейм с информацией о скорости ветра
    city_1_wind_spd = [['wind_day_speed', city_1_forecast[0]['wind_day_speed']]]
    city_1_wind_spd_df = pd.DataFrame(city_1_wind_spd, 
                                    columns=['wind_speed', 'value'])
    
    # создаём и настраиваем фигуру для графика скорости ветра
    city_1_wind_spd_graph = px.bar(city_1_wind_spd_df, x = 'wind_speed', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_1_wind_spd_df))
    city_1_wind_spd_graph.update_layout(width = 400, height = 400, title = city_1)

    # создаём датафрейм с информацией о вероятности осадков и льда
    city_1_probabilities = [['rain_day_probability', city_1_forecast[0]['rain_day_probability']],
                            ['snow_day_probability', city_1_forecast[0]['snow_day_probability']],
                            ['ice_day_probability', city_1_forecast[0]['ice_day_probability']]]
    city_1_probabilities_df = pd.DataFrame(city_1_probabilities, 
                                    columns=['metrics', 'probability'])
    
    # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
    city_1_probabilities_graph = px.bar(city_1_probabilities_df, x = 'metrics', y = 'probability',
                             color_discrete_sequence = ['#9467bd']*len(city_1_probabilities_df))
    city_1_probabilities_graph.update_layout(width = 400, height = 400, title = city_1)

    # создаём датафрейм с информацией о уф-индексе
    city_1_uv_index = [['uv_index', city_1_forecast[0]['uv_index']]]
    city_1_uv_index_df = pd.DataFrame(city_1_uv_index, 
                                    columns=['uv_index', 'value'])
    
    # создаём и настраиваем фигуру для графика с информацией об уф-индексе
    city_1_uv_index_graph = px.bar(city_1_uv_index_df, x = 'uv_index', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_1_uv_index_df))
    city_1_uv_index_graph.update_layout(width = 400, height = 400, title = city_1)

    if dropdown_value == 'Температура':
        return city_1_temp_graph
    
    elif dropdown_value == 'Влажность':
        return city_1_humidity_graph
    
    elif dropdown_value == 'Скорость ветра':
        return city_1_wind_spd_graph
    
    elif dropdown_value == 'Вероятность осадков и льда':
        return city_1_probabilities_graph
    
    elif dropdown_value == 'УФ-индекс':
        return city_1_uv_index_graph

#callback, который строит графики для 2 города
@app.callback(Output(component_id='city_2_graph',
                     component_property='figure'),
            [Input(component_id='submit_cities',
                  component_property='n_clicks'),
            Input(component_id='city_2_dropdown',
                  component_property='value')],
            State(component_id='city_2_input', 
           component_property='value'),
            prevent_initial_call = True)

def create_graphic_2(n_clicks, dropdown_value, city_2):
    global api_key
    global key_by_city_api_url

    get_info = WeatherConditionManager(api_key, key_by_city_api_url)
    city_2_forecast = get_info.get_weather_info_1day(city_2)
    
    # создаём датафрейм с информацией о максимальной и минимальной температуре
    city_2_temp = [['minimal_temp', city_2_forecast[0]['minimal_temp']], 
                   ['maximal_temp', city_2_forecast[0]['maximal_temp']]]
    city_2_temp_df = pd.DataFrame(city_2_temp, 
                                columns=['temp', 'value'])
    
    # создаём и настраиваем фигуру для графика температуры
    city_2_temp_graph = px.bar(city_2_temp_df, x = 'temp', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_2_temp_df))
    city_2_temp_graph.update_layout(width = 400, height = 400,
                                    title = city_2)
    
    # создаём датафрейм с информацией о максимальной и минимальной влажности
    city_2_humidity = [['humidity_day_minimum', city_2_forecast[0]['humidity_day_minimum']], 
                    ['humidity_day_maximum', city_2_forecast[0]['humidity_day_maximum']]]
    city_2_humidity_df = pd.DataFrame(city_2_humidity, 
                                    columns=['humidity', 'value'])
    
    # создаём и настраиваем фигуру для графика влажности
    city_2_humidity_graph = px.bar(city_2_humidity_df, x = 'humidity', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_2_humidity_df))
    city_2_humidity_graph.update_layout(width = 400, height = 400, title = city_2)

    # создаём датафрейм с информацией о скорости ветра
    city_2_wind_spd = [['wind_day_speed', city_2_forecast[0]['wind_day_speed']]]
    city_2_wind_spd_df = pd.DataFrame(city_2_wind_spd, 
                                    columns=['wind_speed', 'value'])
    
    # создаём и настраиваем фигуру для графика скорости ветра
    city_2_wind_spd_graph = px.bar(city_2_wind_spd_df, x = 'wind_speed', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_2_wind_spd_df))
    city_2_wind_spd_graph.update_layout(width = 400, height = 400, title = city_2)

    # создаём датафрейм с информацией о вероятности осадков и льда
    city_2_probabilities = [['rain_day_probability', city_2_forecast[0]['rain_day_probability']],
                            ['snow_day_probability', city_2_forecast[0]['snow_day_probability']],
                            ['ice_day_probability', city_2_forecast[0]['ice_day_probability']]]
    city_2_probabilities_df = pd.DataFrame(city_2_probabilities, 
                                    columns=['metrics', 'probability'])
    
    # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
    city_2_probabilities_graph = px.bar(city_2_probabilities_df, x = 'metrics', y = 'probability',
                             color_discrete_sequence = ['#9467bd']*len(city_2_probabilities_df))
    city_2_probabilities_graph.update_layout(width = 400, height = 400, title = city_2)

    # создаём датафрейм с информацией о уф-индексе
    city_2_uv_index = [['uv_index', city_2_forecast[0]['uv_index']]]
    city_2_uv_index_df = pd.DataFrame(city_2_uv_index, 
                                    columns=['uv_index', 'value'])
    
    # создаём и настраиваем фигуру для графика с информацией об уф-индексе
    city_2_uv_index_graph = px.bar(city_2_uv_index_df, x = 'uv_index', y = 'value',
                             color_discrete_sequence = ['#9467bd']*len(city_2_uv_index_df))
    city_2_uv_index_graph.update_layout(width = 400, height = 400, title = city_2)

    if dropdown_value == 'Температура':
        return city_2_temp_graph
    
    elif dropdown_value == 'Влажность':
        return city_2_humidity_graph
    
    elif dropdown_value == 'Скорость ветра':
        return city_2_wind_spd_graph
    
    elif dropdown_value == 'Вероятность осадков и льда':
        return city_2_probabilities_graph
    
    elif dropdown_value == 'УФ-индекс':
        return city_2_uv_index_graph

#callback, отвечающий за отображение/скрытие выпадающего списка для 1 города
@app.callback(Output(component_id='dropdown_container_1',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_dropdown_1(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие выпадающего списка для 2 города
@app.callback(Output(component_id='dropdown_container_2',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_dropdown_2(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания выпадающего списка для 1 города
@app.callback(Output(component_id='dropdown_description_1',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_dropdown_description_1(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания выпадающего списка для 2 города
@app.callback(Output(component_id='dropdown_description_2',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_dropdown_description_2(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания радиоэлементов (выбор, на сколько дней отображается прогноз)
@app.callback(Output(component_id='radio_items_description',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_radioitems_description(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие радиоэлементов (выбор, на сколько дней отображается прогноз)
@app.callback(Output(component_id='radio_items_container',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_radioitems(n_clicks):
    if n_clicks != 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

if __name__ == '__main__':
    app.run(debug=True)