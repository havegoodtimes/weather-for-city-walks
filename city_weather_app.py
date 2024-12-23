import json
import requests
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


forecast_hourly_api_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/'
api_key = 'qV7vDxXTitSMqoxec5n77w5D5txhR7Kk'
city_info_api_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'

class WeatherConditionManager:
    def __init__(self, api_key, city_info_api_url):
        self.api_key = api_key
        self.city_info_api_url = city_info_api_url
        self.weather_cache = {}
        self.city_coordinates_cache = {}
        #Режим отладки, при котором загрузка происходит из файла 
        #(без использования api), для обхода лимита на количество вызовов у accuweather api
        self.debug_mode = True
    
    def get_location_key_by_city(self, city):
        if self.debug_mode:
            return 'code'
        
        city = city.lower()
        city_info = requests.get(f"{self.city_info_api_url}?apikey={self.api_key}&q={city}", params = 'Key')
        city_data = city_info.json()

        location_key = city_data[0]['Key']
        return location_key
    
    def get_city_coordinates(self, city):
        city = city.lower()
        city_coordinates = self.city_coordinates_cache.get(city) 
        if city_coordinates != None:
            return city_coordinates
        
        if self.debug_mode:
            if city == 'moscow':
                coordinates = [55.752,37.619]
                self.city_coordinates_cache[city] = coordinates
                return coordinates
            elif city == 'dubai':
                coordinates = [25.271,55.313]
                self.city_coordinates_cache[city] = coordinates
                return coordinates
            elif city == 'nyc':
                coordinates = [40.779,-73.969]
                self.city_coordinates_cache[city] = coordinates
                return coordinates
            elif city == 'amsterdam':
                coordinates = [52.372,4.9]
                self.city_coordinates_cache[city] = coordinates
                return coordinates

            elif city == 'shanghai':
                coordinates = [31.232,121.444]
                self.city_coordinates_cache[city] = coordinates
                return coordinates
        else:
            city_info = requests.get(f"{self.city_info_api_url}?apikey={self.api_key}&q={city}")
            if city_info.status_code == 200:
                if city_info.json() == []:
                    return [0, 0]
                city_data = city_info.json()

                lat = city_data[0]["GeoPosition"]["Latitude"]
                lon = city_data[0]["GeoPosition"]["Longitude"]
                coordinates = [lat, lon]
                self.city_coordinates_cache[city] = coordinates
                return coordinates

    def get_weather_info_5days(self, city):
        city = city.lower()
        forecast_api_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/'
        city_data = self.weather_cache.get(city)
        if city_data != None:
            return city_data
        
        if self.debug_mode == True:
            with open(f'C:/Users/Niko/Desktop/python_contest/Python_project_3/{city}_forecast_5days.json', 'r') as file:
                weather_data = json.load(file)
        else:
            location_key = self.get_location_key_by_city(city)    
            weather_info = requests.get(f'{forecast_api_url}{location_key}?apikey={self.api_key}&details=true&metric=true')
            weather_data = weather_info.json()

        weather_info_list = []
        for i in range(0, 5, 2):
            minimal_temp = weather_data["DailyForecasts"][i]["Temperature"]["Minimum"]["Value"]
            maximal_temp = weather_data["DailyForecasts"][i]["Temperature"]["Maximum"]["Value"]
            humidity_day_minimum = weather_data["DailyForecasts"][i]["Day"]["RelativeHumidity"]["Minimum"]
            humidity_day_maximum = weather_data["DailyForecasts"][i]["Day"]["RelativeHumidity"]["Maximum"]
            wind_day_speed = weather_data["DailyForecasts"][i]["Day"]["Wind"]["Speed"]["Value"]
            rain_day_probability = weather_data["DailyForecasts"][i]["Day"]["RainProbability"]
            snow_day_probability = weather_data["DailyForecasts"][i]["Day"]["SnowProbability"]
            ice_day_probability = weather_data["DailyForecasts"][i]["Day"]["IceProbability"]
            uv_index = weather_data["DailyForecasts"][i]['AirAndPollen'][5]["Value"]
            date = weather_data["DailyForecasts"][i]["Date"]

            weather_info_list.append({'date': date,
                            'minimal_temp': minimal_temp, 
                            'maximal_temp' : maximal_temp, 
                            'humidity_day_minimum' : humidity_day_minimum, 
                            'humidity_day_maximum' : humidity_day_maximum, 
                            'wind_day_speed' : wind_day_speed, 
                            'rain_day_probability' : rain_day_probability, 
                            'snow_day_probability' : snow_day_probability,
                            'ice_day_probability' : ice_day_probability, 
                            'uv_index' : uv_index})
        
        self.weather_cache[city] = weather_info_list
        return weather_info_list
        
    def create_weather_dataframe(self, city):
        weather_info_list = self.get_weather_info_5days(city)
        date_list = []
        minimal_temp_list = []
        maximal_temp_list = []
        humidity_day_minimum_list = []
        humidity_day_maximum_list = []
        wind_day_speed_list = []
        rain_day_probability_list = []
        snow_day_probability_list = []
        ice_day_probability_list = []
        uv_index_list = []

        for weather_info in weather_info_list:
            date_list.append(weather_info['date'])
            minimal_temp_list.append(weather_info['minimal_temp'])
            maximal_temp_list.append(weather_info['maximal_temp'])
            humidity_day_minimum_list.append(weather_info['humidity_day_minimum'])
            humidity_day_maximum_list.append(weather_info['humidity_day_maximum'])
            wind_day_speed_list.append(weather_info['wind_day_speed'])
            rain_day_probability_list.append(weather_info['rain_day_probability'])
            snow_day_probability_list.append(weather_info['snow_day_probability'])
            ice_day_probability_list.append(weather_info['ice_day_probability'])
            uv_index_list.append(weather_info['uv_index'])

        weather_forecast_df = pd.DataFrame({'index' : [0, 1, 2],
                                            'date' : date_list,
                                            'minimal_temp' : minimal_temp_list,
                                            'maximal_temp' : maximal_temp_list,
                                            'humidity_day_minimum' : humidity_day_minimum_list,
                                            'humidity_day_maximum' : humidity_day_maximum_list,
                                            'wind_day_speed' : wind_day_speed_list,
                                            'rain_day_probability' : rain_day_probability_list,
                                            'snow_day_probability' : snow_day_probability_list,
                                            'ice_day_probability' : ice_day_probability_list,
                                            'uv_index' : uv_index_list})
        

        return weather_forecast_df

    def check_bad_weather_by_city(self, city):
        weather_info = (self.get_weather_info_5days(city))[0]

        if (weather_info['minimal_temp'] < -10.0 or 
            weather_info['maximal_temp'] > 30.0 or
            weather_info['wind_day_speed'] > 36.0 or
            weather_info['rain_day_probability'] > 60 or 
            weather_info['snow_day_probability'] > 60 or
            weather_info['ice_day_probability'] > 60 or
            weather_info['uv_index'] > 7): 

            status = 'Завтра плохая погода для прогулки'
            return status
        else:
            status = 'Завтра хорошая погода для прогулки'
            return status


app = Dash()
get_info = WeatherConditionManager(api_key, city_info_api_url)

app.layout = [
            html.Div(id = 'introduction',
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
            html.Div(id = 'input_container_3', children=[dcc.Input(id='city_3_input',
                  placeholder='3 город',
                  type = 'text',
                  value = ''
              )]),
            html.Div(id = 'dropdown_description_3',
                  children='Выберите интересующие метрики прогноза погода:'),
            html.Div(id = 'dropdown_container_3',
                       children = [dcc.Dropdown(id = 'city_3_dropdown',
                           options=['Температура', 'Влажность', 'Скорость ветра',
                                    'Вероятность осадков и льда', 'УФ-индекс'],
                                    value = 'Температура')]),
            html.Div(id = 'graph_container_3',children = [dcc.Graph(id='city_3_graph',
                  figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 3',
                'width' : 400,
                'height' : 400
            }}
              )]),
            html.Div(id = 'input_container_4', children=[dcc.Input(id='city_4_input',
                  placeholder='4 город',
                  type = 'text',
                  value = ''
              )]),
            html.Div(id = 'dropdown_description_4',
                  children='Выберите интересующие метрики прогноза погода:'),
            html.Div(id = 'dropdown_container_4',
                       children = [dcc.Dropdown(id = 'city_4_dropdown',
                           options=['Температура', 'Влажность', 'Скорость ветра',
                                    'Вероятность осадков и льда', 'УФ-индекс'],
                                    value = 'Температура')]),
            html.Div(id = 'graph_container_4',children = [dcc.Graph(id='city_4_graph',
                  figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 4',
                'width' : 400,
                'height' : 400
            }}
              )]),
            html.Div(id = 'input_container_5', children=[dcc.Input(id='city_5_input',
                  placeholder='5 город',
                  type = 'text',
                  value = ''
              )]),
            html.Div(id = 'dropdown_description_5',
                  children='Выберите интересующие метрики прогноза погода:'),
            html.Div(id = 'dropdown_container_5',
                       children = [dcc.Dropdown(id = 'city_5_dropdown',
                           options=['Температура', 'Влажность', 'Скорость ветра',
                                    'Вероятность осадков и льда', 'УФ-индекс'],
                                    value = 'Температура')]),
            html.Div(id = 'graph_container_5',children = [dcc.Graph(id='city_5_graph',
                  figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 5',
                'width' : 400,
                'height' : 400
            }}
              )]),
            html.Div(html.Button('Добавить дополнительные города', 
                                 id = 'add_city_input', n_clicks=0)),
            html.Div(html.Button('Отправить', id = 'submit_cities', n_clicks=0)),
            html.Div(id = 'map_container', children=[dcc.Graph(id='map', 
                                                               figure={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 5',
                'width' : 400,
                'height' : 400
            }})
                                                               ])]
            

#callback, отвечающий за отображение/скрытие 1 строки на странице

@app.callback(Output(component_id='introduction',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_introduction(n_clicks):
    if n_clicks != 0:
        return {'display' : 'none'}
    return {'display' : 'block'}

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
    global city_info_api_url
    global get_info
    
    city_1_weather_df = get_info.create_weather_dataframe(city_1)

    if radio_item_value == '1_day':
        days = 1
    elif radio_item_value == '3_day':
        days = 2
    elif radio_item_value == '5_day':
        days = 3
    
    # создаём и настраиваем фигуру для графика температуры
    city_1_temp_graph = go.Figure(data = [go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['minimal_temp'],
                                   name = "Минимальная<br>температура"),
                                   go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['maximal_temp'],
                                   name = 'Максимальная<br>температура')])
    city_1_temp_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>температура"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Температура (Цельсии)")))
    
    # создаём и настраиваем фигуру для графика влажности
    city_1_humidity_graph = go.Figure(data = [go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['humidity_day_minimum'],
                                   name = "Минимальная<br>влажность"),
                                   go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['humidity_day_maximum'],
                                   name = "Максимальная<br>влажность")])
    city_1_humidity_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>влажность"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Влажность (%)")))
    
    # создаём и настраиваем фигуру для графика скорости ветра
    city_1_wind_spd_graph = go.Figure(data = [go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['wind_day_speed'],
                                   name = "Скорость<br>ветра")])
                                   
    city_1_wind_spd_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Скорость ветра"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Скорость (м/c)")))
    
    # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
    city_1_probabilities_graph = go.Figure(data = [go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['rain_day_probability'],
                                   name = "Дождь"),
                                   go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['snow_day_probability'],
                                   name = "Снег"),
                                   go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['ice_day_probability'],
                                   name = "Лёд")])
    city_1_probabilities_graph.update_layout(width = 600, height = 600,
                                title =  dict(text="Вероятность осадков и льда"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Вероятность (%)")))

    # создаём и настраиваем фигуру для графика с информацией об уф-индексе
    city_1_uv_index_graph = go.Figure(data = [go.Bar(
                                   x = city_1_weather_df.query(f'index < {days}')['date'], 
                                   y = city_1_weather_df.query(f'index < {days}')['uv_index'],
                                   name = "УФ-индекс")])
    city_1_uv_index_graph.update_layout(width = 600, height = 600,
                                title = dict(text="УФ-индекс"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Уровень")))

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
                  component_property='value'),
            Input(component_id='radio_items',
                  component_property='value')],
            State(component_id='city_2_input', 
           component_property='value'),
            prevent_initial_call = True)

def create_graphic_2(n_clicks, dropdown_value, radio_item_value, city_2):
    global api_key
    global city_info_api_url
    global get_info

    city_2_weather_df = get_info.create_weather_dataframe(city_2)

    if radio_item_value == '1_day':
        days = 1
    elif radio_item_value == '3_day':
        days = 2
    elif radio_item_value == '5_day':
        days = 3
    
    # создаём и настраиваем фигуру для графика температуры
    city_2_temp_graph = go.Figure(data = [go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['minimal_temp'],
                                   name = "Минимальная<br>температура"),
                                   go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['maximal_temp'],
                                   name = "Максимальная<br>температура")])
    city_2_temp_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>температура"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Температура (Цельсии)")))
    
    # создаём и настраиваем фигуру для графика влажности
    city_2_humidity_graph = go.Figure(data = [go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['humidity_day_minimum'],
                                   name = "Минимальная<br>влажность"),
                                   go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['humidity_day_maximum'],
                                   name = "Максимальная<br>влажность")])
    city_2_humidity_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>влажность"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Влажность (%)")))
    
    # создаём и настраиваем фигуру для графика скорости ветра
    city_2_wind_spd_graph = go.Figure(data = [go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['wind_day_speed'],
                                   name = "Скорость<br>ветра")])
    city_2_wind_spd_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Скорость ветра"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Скорость (м/c)")))
    
    # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
    city_2_probabilities_graph = go.Figure(data = [go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['rain_day_probability'],
                                   name = "Дождь"),
                                   go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['snow_day_probability'],
                                   name = "Снег"),
                                   go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['ice_day_probability'],
                                   name = "Лёд")])
    city_2_probabilities_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Вероятность осадков и льда"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Вероятность (%)")))

    # создаём и настраиваем фигуру для графика с информацией об уф-индексе
    city_2_uv_index_graph = go.Figure(data = [go.Bar(
                                   x = city_2_weather_df.query(f'index < {days}')['date'], 
                                   y = city_2_weather_df.query(f'index < {days}')['uv_index'],
                                   name = "УФ-индекс")])
    city_2_uv_index_graph.update_layout(width = 600, height = 600,
                                title = dict(text="УФ-индекс"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Уровень")))

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

#callback, отвечающий за отображение/скрытие поля ввода для третьего города
@app.callback(Output(component_id='input_container_3',
                     component_property='style'),
            Input(component_id='add_city_input',
          component_property='n_clicks'))

def hide_input_3(n_clicks):
    if n_clicks > 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие поля ввода для четвёртого города
@app.callback(Output(component_id='input_container_4',
                     component_property='style'),
            Input(component_id='add_city_input',
          component_property='n_clicks'))

def hide_input_4(n_clicks):
    if n_clicks > 1:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие поля ввода для четвёртого города
@app.callback(Output(component_id='input_container_5',
                     component_property='style'),
            Input(component_id='add_city_input',
          component_property='n_clicks'))

def hide_input_5(n_clicks):
    if n_clicks > 2:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания выпадающего списка для 3 города
@app.callback(Output(component_id='dropdown_description_3',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_description_3(submit_clicks, add_city_clicks):
    if submit_clicks >0 and add_city_clicks > 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие выпадающего списка для 3 города
@app.callback(Output(component_id='dropdown_container_3',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_3(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания выпадающего списка для 4 города
@app.callback(Output(component_id='dropdown_description_4',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_description_4(submit_clicks, add_city_clicks):
    if submit_clicks >0 and add_city_clicks > 1:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие выпадающего списка для 4 города
@app.callback(Output(component_id='dropdown_container_4',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_4(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 1:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие описания выпадающего списка для 5 города
@app.callback(Output(component_id='dropdown_description_5',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_description_5(submit_clicks, add_city_clicks):
    if submit_clicks >0 and add_city_clicks > 2:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие выпадающего списка для 5 города
@app.callback(Output(component_id='dropdown_container_5',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_dropdown_5(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 2:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие графика для 3 города
@app.callback(Output(component_id='graph_container_3',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_graph_3(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие графика для 4 города
@app.callback(Output(component_id='graph_container_4',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_graph_4(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 1:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, отвечающий за отображение/скрытие графика для 5 города
@app.callback(Output(component_id='graph_container_5',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'),
          State(component_id='add_city_input',
                component_property='n_clicks'))

def hide_graph_5(submit_clicks, add_city_clicks):
    if submit_clicks > 0 and add_city_clicks > 2:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, который строит графики для 3 города
@app.callback(Output(component_id='city_3_graph',
                     component_property='figure'),
            [Input(component_id='submit_cities',
                  component_property='n_clicks'),
            Input(component_id='city_3_dropdown',
                  component_property='value'),
            Input(component_id='radio_items',
                  component_property='value')],
            [State(component_id='city_3_input', 
           component_property='value'),
           State(component_id='add_city_input',
                component_property='n_clicks') ],
            prevent_initial_call = True)

def create_graphic_3(submit_clicks, dropdown_value, radio_item_value, city_3, add_city_clicks):
    global api_key
    global city_info_api_url
    global get_info

    if submit_clicks > 0 and add_city_clicks > 0:
    
        city_3_weather_df = get_info.create_weather_dataframe(city_3)


        if radio_item_value == '1_day':
            days = 1
        elif radio_item_value == '3_day':
            days = 2
        elif radio_item_value == '5_day':
            days = 3
        
        # создаём и настраиваем фигуру для графика температуры
        city_3_temp_graph = go.Figure(data = [go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['minimal_temp'],
                                    name = "Минимальная<br>температура"),
                                    go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['maximal_temp'],
                                    name = "Максимальная<br>температура")])
        city_3_temp_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>температура"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Температура (Цельсии)")))
        
        # создаём и настраиваем фигуру для графика влажности
        city_3_humidity_graph = go.Figure(data = [go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['humidity_day_minimum'],
                                    name = "Минимальная<br>влажность"),
                                    go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['humidity_day_maximum'],
                                    name = "Максимальная<br>влажность"
                                    )])
        city_3_humidity_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>влажность"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Влажность (%)")))
        
        # создаём и настраиваем фигуру для графика скорости ветра
        city_3_wind_spd_graph = go.Figure(data = [go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['wind_day_speed'],
                                    name = "Скорость<br>ветра")])
        city_3_wind_spd_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Скорость ветра"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Скорость (м/c)")))
        
        # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
        city_3_probabilities_graph = go.Figure(data = [go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['rain_day_probability'],
                                    name = "Дождь"),
                                    go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['snow_day_probability'],
                                    name = "Снег"),
                                    go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['ice_day_probability'],
                                    name = "Лёд")])
        city_3_probabilities_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Вероятность осадков и льда"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Вероятность (%)")))

        # создаём и настраиваем фигуру для графика с информацией об уф-индексе
        city_3_uv_index_graph = go.Figure(data = [go.Bar(
                                    x = city_3_weather_df.query(f'index < {days}')['date'], 
                                    y = city_3_weather_df.query(f'index < {days}')['uv_index'],
                                    name = "УФ-индекс")])
        city_3_uv_index_graph.update_layout(width = 600, height = 600,
                                title = dict(text="УФ-индекс"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Уровень")))

        if dropdown_value == 'Температура':
            return city_3_temp_graph
        
        elif dropdown_value == 'Влажность':
            return city_3_humidity_graph
        
        elif dropdown_value == 'Скорость ветра':
            return city_3_wind_spd_graph
        
        elif dropdown_value == 'Вероятность осадков и льда':
            return city_3_probabilities_graph
        
        elif dropdown_value == 'УФ-индекс':
            return city_3_uv_index_graph
        
    else:
        fig={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 3',
                'width' : 400,
                'height' : 400
            }}
        return fig
    
#callback, который строит графики для 4 города
@app.callback(Output(component_id='city_4_graph',
                     component_property='figure'),
            [Input(component_id='submit_cities',
                  component_property='n_clicks'),
            Input(component_id='city_4_dropdown',
                  component_property='value'),
            Input(component_id='radio_items',
                  component_property='value')],
            [State(component_id='city_4_input', 
           component_property='value'),
           State(component_id='add_city_input',
                component_property='n_clicks') ],
            prevent_initial_call = True)

def create_graphic_4(submit_clicks, dropdown_value, radio_item_value, city_4, add_city_clicks):
    global api_key
    global city_info_api_url
    global get_info

    if submit_clicks > 0 and add_city_clicks > 1:
    
        city_4_weather_df = get_info.create_weather_dataframe(city_4)


        if radio_item_value == '1_day':
            days = 1
        elif radio_item_value == '3_day':
            days = 2
        elif radio_item_value == '5_day':
            days = 3
        
        # создаём и настраиваем фигуру для графика температуры
        city_4_temp_graph = go.Figure(data = [go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['minimal_temp'],
                                    name = "Минимальная<br>температура"),
                                    go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['maximal_temp'],
                                    name = "Максимальная<br>температура")])
        city_4_temp_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>температура"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Температура (Цельсии)")))
        
        # создаём и настраиваем фигуру для графика влажности
        city_4_humidity_graph = go.Figure(data = [go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['humidity_day_minimum'],
                                    name = "Минимальная<br>влажность"),
                                    go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['humidity_day_maximum'],
                                    name = "Максимальная<br>влажность")])
        city_4_humidity_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>влажность"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Влажность (%)")))
        
        # создаём и настраиваем фигуру для графика скорости ветра
        city_4_wind_spd_graph = go.Figure(data = [go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['wind_day_speed'],
                                    name = "Скорость<br>ветра")])
        city_4_wind_spd_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Скорость ветра"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Скорость (м/c)")))
        
        # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
        city_4_probabilities_graph = go.Figure(data = [go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['rain_day_probability'],
                                    name = "Дождь"),
                                    go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['snow_day_probability'],
                                    name = "Снег"),
                                    go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['ice_day_probability'],
                                    name = "Лёд")])
        city_4_probabilities_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Вероятность осадков и льда"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Вероятность (%)")))

        # создаём и настраиваем фигуру для графика с информацией об уф-индексе
        city_4_uv_index_graph = go.Figure(data = [go.Bar(
                                    x = city_4_weather_df.query(f'index < {days}')['date'], 
                                    y = city_4_weather_df.query(f'index < {days}')['uv_index'],
                                    name = "УФ-индекс")])
        city_4_uv_index_graph.update_layout(width = 600, height = 600,
                                title = dict(text="УФ-индекс"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Уровень")))

        if dropdown_value == 'Температура':
            return city_4_temp_graph
        
        elif dropdown_value == 'Влажность':
            return city_4_humidity_graph
        
        elif dropdown_value == 'Скорость ветра':
            return city_4_wind_spd_graph
        
        elif dropdown_value == 'Вероятность осадков и льда':
            return city_4_probabilities_graph
        
        elif dropdown_value == 'УФ-индекс':
            return city_4_uv_index_graph
        
    else:
        fig={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 4',
                'width' : 400,
                'height' : 400
            }}
        return fig
    
#callback, который строит графики для 5 города
@app.callback(Output(component_id='city_5_graph',
                     component_property='figure'),
            [Input(component_id='submit_cities',
                  component_property='n_clicks'),
            Input(component_id='city_5_dropdown',
                  component_property='value'),
            Input(component_id='radio_items',
                  component_property='value')],
            [State(component_id='city_5_input', 
           component_property='value'),
           State(component_id='add_city_input',
                component_property='n_clicks') ],
            prevent_initial_call = True)

def create_graphic_5(submit_clicks, dropdown_value, radio_item_value, city_5, add_city_clicks):
    global api_key
    global city_info_api_url
    global get_info

    if submit_clicks > 0 and add_city_clicks > 2:
    
        city_5_weather_df = get_info.create_weather_dataframe(city_5)


        if radio_item_value == '1_day':
            days = 1
        elif radio_item_value == '3_day':
            days = 2
        elif radio_item_value == '5_day':
            days = 3
        
        # создаём и настраиваем фигуру для графика температуры
        city_5_temp_graph = go.Figure(data = [go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['minimal_temp'],
                                    name = "Минимальная<br>температура"),
                                    go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['maximal_temp'],
                                    name = "Максимальная<br>температура")])
        city_5_temp_graph.update_layout(width = 600, height = 600,
                                    title = dict(text="Максимальная и минимальная<br>температура"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Температура (Цельсии)")))
        
        # создаём и настраиваем фигуру для графика влажности
        city_5_humidity_graph = go.Figure(data = [go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['humidity_day_minimum'],
                                    name = "Минимальная<br>влажность"),
                                    go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['humidity_day_maximum'],
                                    name = "Максимальная<br>влажность")])
        city_5_humidity_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Максимальная и минимальная<br>влажность"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Влажность (%)")))
        
        # создаём и настраиваем фигуру для графика скорости ветра
        city_5_wind_spd_graph = go.Figure(data = [go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['wind_day_speed'],
                                    name = "Скорость<br>ветра")])
        city_5_wind_spd_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Скорость ветра"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Скорость (м/c)")))
        
        # создаём и настраиваем фигуру для графика с вероятностями осадков и льда
        city_5_probabilities_graph = go.Figure(data = [go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['rain_day_probability'],
                                    name = "Дождь"),
                                    go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['snow_day_probability'],
                                    name = "Снег"),
                                    go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['ice_day_probability'],
                                    name = "Снег")])
        city_5_probabilities_graph.update_layout(width = 600, height = 600,
                                title = dict(text="Вероятность осадков и льда"),
                                xaxis = dict(title = dict(text = "Дата")),
                                yaxis = dict(title = dict(text = "Вероятность (%)")))

        # создаём и настраиваем фигуру для графика с информацией об уф-индексе
        city_5_uv_index_graph = go.Figure(data = [go.Bar(
                                    x = city_5_weather_df.query(f'index < {days}')['date'], 
                                    y = city_5_weather_df.query(f'index < {days}')['uv_index'],
                                    name = "УФ-индекс")])
        city_5_uv_index_graph.update_layout(width = 600, height = 600,
                                    title = city_5)

        if dropdown_value == 'Температура':
            return city_5_temp_graph
        
        elif dropdown_value == 'Влажность':
            return city_5_humidity_graph
        
        elif dropdown_value == 'Скорость ветра':
            return city_5_wind_spd_graph
        
        elif dropdown_value == 'Вероятность осадков и льда':
            return city_5_probabilities_graph
        
        elif dropdown_value == 'УФ-индекс':
            return city_5_uv_index_graph
        
    else:
        fig={'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'h'},
            ],
            'layout': {
                'title': 'Barchart 5',
                'width' : 400,
                'height' : 400
            }}
        return fig

#callback, отвечающий за отображение/скрытие карты с городами
@app.callback(Output(component_id='map_container',
                     component_property='style'),
            Input(component_id='submit_cities',
          component_property='n_clicks'))

def hide_map(submit_clicks):
    if submit_clicks > 0:
        return {'display' : 'block'}
    return {'display' : 'none'}

#callback, который создаёт карту с городами
@app.callback(Output(component_id='map',
                     component_property='figure'),
            Input(component_id='submit_cities',
                  component_property='n_clicks'),
            [State(component_id='city_1_input', 
           component_property='value'),
           State(component_id='city_2_input', 
           component_property='value'),
           State(component_id='city_3_input', 
           component_property='value'),
           State(component_id='city_4_input', 
           component_property='value'),
           State(component_id='city_5_input', 
           component_property='value'),
           State(component_id='add_city_input',
                component_property='n_clicks') ],
            prevent_initial_call = True)

def create_graphic_5(submit_clicks, city_1,
                     city_2, city_3, city_4, city_5, add_city_clicks):
    global get_info
    
    if submit_clicks > 0:
        city_1_coordinates = get_info.get_city_coordinates(city_1)
        city_2_coordinates = get_info.get_city_coordinates(city_2)
        lat_list = [city_1_coordinates[0], city_2_coordinates[0]]
        lon_list = [city_1_coordinates[1], city_2_coordinates[1]]
        cities_list = [city_1, city_2]
        city_1_recomendation = get_info.check_bad_weather_by_city(city_1)
        city_2_recomendation = get_info.check_bad_weather_by_city(city_2)
        recomendations_list = [city_1_recomendation, city_2_recomendation]
        if add_city_clicks > 0:
            city_3_coordinates = get_info.get_city_coordinates(city_3)
            lat_list.append(city_3_coordinates[0])
            lon_list.append(city_3_coordinates[1])
            cities_list.append(city_3)
            city_3_recomendation = get_info.check_bad_weather_by_city(city_3)
            recomendations_list.append(city_3_recomendation)
        if add_city_clicks > 1:
            city_4_coordinates = get_info.get_city_coordinates(city_4)
            lat_list.append(city_4_coordinates[0])
            lon_list.append(city_4_coordinates[1])
            cities_list.append(city_4)
            city_4_recomendation = get_info.check_bad_weather_by_city(city_4)
            recomendations_list.append(city_4_recomendation)
        if add_city_clicks > 2:
            city_5_coordinates = get_info.get_city_coordinates(city_5)
            lat_list.append(city_5_coordinates[0])
            lon_list.append(city_5_coordinates[1])
            cities_list.append(city_5)
            city_5_recomendation = get_info.check_bad_weather_by_city(city_5)
            recomendations_list.append(city_5_recomendation)
        
        fig = go.Figure(go.Scattermap(
            mode = 'markers+text+lines',
            lat = lat_list, lon =  lon_list,
            marker = {'size' : 20, 'symbol' : 'marker'},
            text = cities_list, textposition='bottom right',
            hovertext = recomendations_list,
            hoverinfo="text"
        ))
        fig.update_layout(width = 1000, height = 800,
                          hoverlabel = dict(font_size = 18))
    return fig



if __name__ == '__main__':
    app.run(debug=True)