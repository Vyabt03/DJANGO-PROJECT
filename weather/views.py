from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import cohere
from datetime import datetime

API_KEY = '8fc432f6ff376da749c6c93bc48e8337'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'
cohere_client = cohere.Client('DCEsndJTXUPph0wTmWd5SUil7HWLhJGWQkQsX3hO')

def get_weather_tip(description):
    prompt = f"Provide a short, practical weather tip for conditions like: {description}. The tip should be a complete sentence, clear and useful, and limited to 35 words or 178 characters."

    try:
        response = cohere_client.generate(
            model='command',
            prompt=prompt,
            max_tokens=40,
            temperature=0.5,
            stop_sequences=["\n"]
        )
        tip = response.generations[0].text.strip()
        return tip if tip else "Stay prepared and check your local weather updates regularly."
    except Exception:
        return "Stay prepared and check your local weather updates regularly."

def weather_forecast(request):
    city = request.GET.get('city', '')
    data = None
    error = None

    if city:
        current_url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"

        current_res = requests.get(current_url)
        forecast_res = requests.get(forecast_url)

        if current_res.status_code == 200 and forecast_res.status_code == 200:
            current = current_res.json()
            forecast = forecast_res.json()

            current_description = current['weather'][0]['description']

            data = {
                'city': current['name'],
                'current': {
                    'temp': current['main']['temp'],
                    'description': current_description,
                    'icon': current['weather'][0]['icon'],
                    'humidity': current['main']['humidity'],
                    'wind_speed': current['wind']['speed'],
                },
                'forecast': [],
                'tip': get_weather_tip(current_description),
            }

            for i in range(0, 40, 8):  
                day = forecast['list'][i]
                date_obj = datetime.strptime(day['dt_txt'], '%Y-%m-%d %H:%M:%S')
                day_name = date_obj.strftime('%A') 

                data['forecast'].append({
                    'day': day_name,
                    'date': date_obj.strftime('%a, %b %d'),
                    'temp': day['main']['temp'],
                    'description': day['weather'][0]['description'],
                    'icon': day['weather'][0]['icon'],
                })
        else:
            error = "City not found. Please enter a valid city name."

    return render(request, 'weather/forecast.html', {'data': data, 'city': city, 'error': error})

class WeatherView(APIView):
    def get(self, request):
        city = request.query_params.get('city', 'London')
        current_url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"

        current_res = requests.get(current_url)
        forecast_res = requests.get(forecast_url)

        if current_res.status_code == 200 and forecast_res.status_code == 200:
            current = current_res.json()
            forecast = forecast_res.json()

            data = {
                'city': current['name'],
                'current': {
                    'temp': current['main']['temp'],
                    'description': current['weather'][0]['description'],
                    'icon': current['weather'][0]['icon'],
                },
                'forecast': []
            }

            for i in range(0, 40, 8):
                day = forecast['list'][i]
                date_obj = datetime.strptime(day['dt_txt'], '%Y-%m-%d %H:%M:%S')
                day_name = date_obj.strftime('%A')

                data['forecast'].append({
                    'day': day_name,
                    'date': date_obj.strftime('%a, %b %d'),  
                    'temp': day['main']['temp'],
                    'description': day['weather'][0]['description'],
                    'icon': day['weather'][0]['icon'],
                })

            return Response(data)
        else:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
