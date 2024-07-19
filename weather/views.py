import requests
from django.shortcuts import render
from django.http import JsonResponse
from .models import CitySearchHistory
from .forms import CitySearchForm
from django.db.models import Count

# Код погоды
WEATHER_CODES = {
    0: 'Ясное небо',
    1: 'Преимущественно ясно',
    2: 'Переменная облачность',
    3: 'Пасмурно',
    45: 'Туман',
    48: 'Отложение изморози',
    51: 'Морось: Легкая',
    53: 'Морось: Умеренная',
    55: 'Морось: Сильная',
    56: 'Ледяная морось: Легкая',
    57: 'Ледяная морось: Сильная',
    61: 'Дождь: Небольшой',
    63: 'Дождь: Умеренный',
    65: 'Дождь: Сильный',
    66: 'Ледяной дождь: Легкий',
    67: 'Ледяной дождь: Сильный',
    71: 'Снегопад: Небольшой',
    73: 'Снегопад: Умеренный',
    75: 'Снегопад: Сильный',
    77: 'Снежная крупа',
    80: 'Ливневый дождь: Небольшой',
    81: 'Ливневый дождь: Умеренный',
    82: 'Ливневый дождь: Сильный',
    85: 'Снегопад с интервалами: Небольшой',
    86: 'Снегопад с интервалами: Сильный',
    95: 'Гроза: Небольшая или умеренная',
    96: 'Гроза с небольшим градом',
    99: 'Гроза с сильным градом'
}


def search_weather(request):
    form = CitySearchForm()
    weather_data = None

    if request.method == 'POST':
        form = CitySearchForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']

            # Проверка наличия города в истории
            city_history, created = CitySearchHistory.objects.get_or_create(city_name=city_name)
            if not created:
                city_history.search_count += 1
                city_history.save()

                # Если город передан в параметрах GET-запроса, выполнить поиск погоды
                if city_name:
                    weather_data = fetch_weather(city_name)

    # Получение истории поиска
    search_history = CitySearchHistory.objects.all().order_by('-search_count')

    return render(request, 'weather/index.html', {
        'form': form,
        'weather_data': weather_data,
        'search_history': search_history
    })


def fetch_weather(city_name):
    # Используем Geonames для получения широты и долготы города
    username = 'temashev'
    geonames_url = f'http://api.geonames.org/searchJSON?q={city_name}&maxRows=1&username={username}'
    response = requests.get(geonames_url)
    if response.status_code == 200 and response.json().get('geonames'):
        geoname = response.json()['geonames'][0]
        latitude = geoname['lat']
        longitude = geoname['lng']

        # Запрос к Open-Meteo API
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_min,temperature_2m_max,weathercode,windspeed_10m_max&timezone=auto"
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json().get('daily', {})
            if weather_data:
                weather_description = WEATHER_CODES.get(weather_data['weathercode'][0], 'Unknown')
                return {
                    'date': weather_data['time'][0],
                    'temperature_min': weather_data['temperature_2m_min'][0],
                    'temperature_max': weather_data['temperature_2m_max'][0],
                    'weather': weather_description,
                    'wind_speed': weather_data['windspeed_10m_max'][0]
                }
    return None


def autocomplete_city(request):
    if 'term' in request.GET:
        term = request.GET.get('term')

        # Автодополнение из API Geonames
        username = 'temashev'
        geonames_url = f'http://api.geonames.org/searchJSON?name_startsWith={term}&maxRows=10&username={username}'
        response = requests.get(geonames_url)
        results = response.json().get('geonames', [])
        city_names = [result['name'] for result in results]
        return JsonResponse(city_names, safe=False)
    return JsonResponse([], safe=False)


def city_search_stats(request):
    stats = CitySearchHistory.objects.values('city_name').annotate(search_count=Count('city_name')).order_by(
        '-search_count')
    return JsonResponse(list(stats), safe=False)
