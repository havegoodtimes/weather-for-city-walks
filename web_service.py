from flask import Flask
from flask import request
from flask import render_template
import requests
import json

class WeatherConditionEstimator:

    def __init__(self, api_key, location_api_url, city_info_api_url, forecast_api_url):
        self.api_key = api_key
        self.location_api_url = location_api_url
        self.city_info_api_url = city_info_api_url
        self.forecast_api_url = forecast_api_url

    def get_location_key_by_coordinates(self, lat, lon):
        try:
            location_info = requests.get(f"{self.location_api_url}?apikey={self.api_key}&q={lat}%2C%20{lon}", params = 'Key')
            if location_info.status_code == 200:
                location_data = location_info.json()
            else:
                return location_info.status_code

            location_key = location_data['Key']
            return location_key
        except:
            return 'error'
    
    def get_location_key_by_city(self, city):
        city = city.lower()
        try:
            city_info = requests.get(f"{self.city_info_api_url}?apikey={self.api_key}&q={city}", params = 'Key')
            if city_info.status_code == 200:
                if city_info.json() == []:
                    return 'wrong_city_error'
                city_data = city_info.json()

                location_key = city_data[0]['Key']
                return location_key
            else:
                return city_info.status_code

        except:
            return 'error'
    
    def get_weather_info_by_coordinates(self, lat, lon):
        try:
            location_key = self.get_location_key_by_coordinates(lat, lon)
            weather_info = requests.get(f'{self.forecast_api_url}{location_key}?apikey={self.api_key}&details=true&metric=true')

            if weather_info.status_code == 200:
                weather_data = weather_info.json()

                minimal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
                maximal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
                humidity_day_minimum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Minimum"]
                humidity_day_maximum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Maximum"]
                wind_day_speed = weather_data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
                rain_day_probability = weather_data["DailyForecasts"][0]["Day"]["RainProbability"]
                snow_day_probability = weather_data["DailyForecasts"][0]["Day"]["SnowProbability"]
                ice_day_probability = weather_data["DailyForecasts"][0]["Day"]["IceProbability"]
                uv_index = weather_data["DailyForecasts"][0]['AirAndPollen'][5]["Value"]

                weather_info_dict = {'minimal_temp': minimal_temp, 
                                    'maximal_temp' : maximal_temp, 
                                    'humidity_day_minimum' : humidity_day_minimum, 
                                    'humidity_day_maximum' : humidity_day_maximum, 
                                    'wind_day_speed' : wind_day_speed, 
                                    'rain_day_probability' : rain_day_probability, 
                                    'snow_day_probability' : snow_day_probability,
                                    'ice_day_probability' : ice_day_probability, 
                                    'uv_index' : uv_index}

                return weather_info_dict

            else:
                return 'error'
        except:
            return 'error'

    def get_weather_info_by_city(self, city):
        try:
            location_key = self.get_location_key_by_city(city)
            if (location_key in [400, 401, 403, 404, 500, 503] or 
                location_key == 'wrong_city_error'):  
                return location_key        
            weather_info = requests.get(f'{self.forecast_api_url}{location_key}?apikey={self.api_key}&details=true&metric=true')
            
            if weather_info.status_code == 200:
                weather_data = weather_info.json()

                minimal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
                maximal_temp = weather_data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
                humidity_day_minimum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Minimum"]
                humidity_day_maximum = weather_data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Maximum"]
                wind_day_speed = weather_data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
                rain_day_probability = weather_data["DailyForecasts"][0]["Day"]["RainProbability"]
                snow_day_probability = weather_data["DailyForecasts"][0]["Day"]["SnowProbability"]
                ice_day_probability = weather_data["DailyForecasts"][0]["Day"]["IceProbability"]
                uv_index = weather_data["DailyForecasts"][0]['AirAndPollen'][5]["Value"]

                weather_info_dict = {'minimal_temp': minimal_temp, 
                                    'maximal_temp' : maximal_temp, 
                                    'humidity_day_minimum' : humidity_day_minimum, 
                                    'humidity_day_maximum' : humidity_day_maximum, 
                                    'wind_day_speed' : wind_day_speed, 
                                    'rain_day_probability' : rain_day_probability, 
                                    'snow_day_probability' : snow_day_probability,
                                    'ice_day_probability' : ice_day_probability, 
                                    'uv_index' : uv_index}

                return weather_info_dict
            
            else:
                return weather_info.status_code

        except:
            return 'error'

    def check_bad_weather_by_coordinates(self, lat, lon):
        try:
            weather_info = self.get_weather_info_by_coordinates(lat, lon)


            if (weather_info['minimal_temp'] < -10.0 or 
                weather_info['maximal_temp'] > 30.0 or
                weather_info['wind_day_speed'] > 36.0 or
                weather_info['rain_day_probability'] > 60 or 
                weather_info['snow_day_probability'] > 60 or
                weather_info['ice_day_probability'] > 60 or
                weather_info['uv_index'] > 7): 
                
                status = 'плохая погода для прогулки'
                return status
            else:
                status = 'хорошая погода для прогулки'
                return status
        except:
            return 'error'

    def check_bad_weather_by_city(self, city):
        try:
            weather_info = self.get_weather_info_by_city(city)
               
            if (weather_info in [400, 401, 403, 404, 500, 503] 
                or weather_info == 'wrong_city_error'):
                return weather_info

            if (weather_info['minimal_temp'] < -10.0 or 
                weather_info['maximal_temp'] > 30.0 or
                weather_info['wind_day_speed'] > 36.0 or
                weather_info['rain_day_probability'] > 60 or 
                weather_info['snow_day_probability'] > 60 or
                weather_info['ice_day_probability'] > 60 or
                weather_info['uv_index'] > 7): 

                status = 'плохая погода для прогулки'
                return status
            else:
                status = 'хорошая погода для прогулки'
                return status
            
        except:
            return 'error'



app = Flask(__name__)
@app.route('/', methods = ['GET', 'POST'])
def weather_recomendation():
    if request.method == 'GET':
        return render_template('form_city.html')
  
    else:
        start_city = request.form['start_city']
        end_city = request.form['end_city']
        # lat = 15.553115
        # lon = 32.537408
        api_key = 'qV7vDxXTitSMqoxec5n77w5D5txhR7Kk'
        location_api_url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
        city_info_api_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
        forecast_api_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/'

        get_info = WeatherConditionEstimator(api_key, location_api_url, city_info_api_url, forecast_api_url)
        start_city_status = get_info.check_bad_weather_by_city(start_city)
        end_city_status = get_info.check_bad_weather_by_city(end_city)

        if start_city_status == 'wrong_city_error' or end_city_status == 'wrong_city_error':
            return "Город не найден. Проверьте, что вы правильно написали название города."
        elif start_city_status == 503 or end_city_status == 503:
            return "Вы достигли лимита запросов. Попробуйте запросить рекомендации завтра."
        elif start_city_status in [401, 403] or end_city_status in [401, 403]:
            return "Нет доступа к сервису прогноза погоды"
        elif start_city_status == 404 or end_city_status == 404:
            return "Произошла ошибка при запросе к сервису прогноза погоды."
        elif start_city_status == 500 or end_city_status == 500:
            return "Сервис прогноза погоды перестал работать"
        elif start_city_status == 400 or end_city_status == 400:
            return "Не найден прогноз погоды для города"
        elif start_city_status == 'error' or end_city_status == 'error':
            return 'Произошла неизвестная ошибка'
        else:
            result = f'{start_city} - {start_city_status}<br/>{end_city} - {end_city_status}'
            return result


if __name__ == '__main__':
    app.run(debug = True)








