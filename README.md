# Django Test Weather App

Это приложение позволяет узнать погоду в городе по запросу и хранит историю поиска.

## Использованные технологии
- Django
- Bootstrap
- Open-meteo API (получение данных о погоде)
- Docker
- SQLite

## Запуск проекта
1. Клонирование репозитория:
```sh
git clone https://github.com/temashev/weather
cd weather_project
```
2. Создание виртуального окружения (файл .env)


3. Запуск Docker
```sh
docker-compose up --build
```


4. Применение миграций
```sh
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```


5. Перейти по адресу http://localhost:8000