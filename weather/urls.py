from django.urls import path
from .views import weather_forecast, WeatherView

urlpatterns = [
    path('', weather_forecast, name='weather-home'),         
    path('api/forecast/', WeatherView.as_view(), name='weather-api'),  # REST API endpoint
]
