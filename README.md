# sibdev_test_2

Тестовое задание #2 для компании Sibdev


# Установка:

```
git clone https://github.com/UncleVasya/sibdev_test_2.git

cd sibdev_test_2

docker-compose up
```

Это запустит веб-сервер + celery-worker + celery-beat.

Для удобства можно запустить сервисы по отдельности в разных терминалах:

```
docker-compose up web
docker-compose up celery-worker
docker-compose up celery-beat
```

При запуске проекта будет создан суперпользователь:
```
email: admin@test.com
Пароль: admin
```

------------------

Для удобства важные команды вынесены в Makefile:

```
* make build
* make run
* make test
* make bash
```

------------------

# Использование

## Swagger

API задокументировано с помощью Swagger. Он доступен по адресу:
http://localhost:8000/api/v1/schema/swagger-ui

## Эндпоинты API

### Регистрация пользователя

```
POST http://localhost:8000/api/v1/user/register/

{
  "email": "admin@test.com",
  "password": "admin"
}
```

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/user/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "admin@test.com",
  "password": "admin"
}'
```

### Авторизация пользователя

```
POST http://localhost:8000/api/v1/user/login/

{
  "email": "admin@test.com",
  "password": "admin"
}
```

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/user/login/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "admin@test.com",
  "password": "admin"
}'
```

Ответ:

```
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5NDA3NTc4MywiaWF0IjoxNjk0MDU0MTgzLCJqdGkiOiI4MjgzMzQzOTc4NjA0ZDA2ODYwMmY2MDI3YTUxZDBjNCIsInVzZXJfaWQiOjJ9.Sw4Fh2RdC_JMgn0bPChVsN8KRVoYdgofB2jolIPUDrE",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk0MDU1OTgzLCJpYXQiOjE2OTQwNTQxODMsImp0aSI6IjZlOTk1YmJlNDY5MjQ3MWM5YWM4Y2RmOTI4ODA2OTY1IiwidXNlcl9pZCI6Mn0.OCYEgbvf8eBdKEh8a3zA0hSwRDEwneirtR007_mDezQ"
}
```

### Добавление пользователем отслеживаемой валюты

Требует авторизацию. Есть проверка на уникальность пары "валюта-пользователь".
```
POST http://localhost:8000/api/v1/currency/user-currency/
```

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/currency/user-currency/' \
  -H 'accept: application/json' \
  -H 'Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk0MDU2NjM4LCJpYXQiOjE2OTQwNTQ4MzgsImp0aSI6IjY2MzUxMjIxNThkZjQ4MmM4NzkwOGUwODUwMGZhZjcxIiwidXNlcl9pZCI6MX0.pwElSZs5G1hOAvsvQb1iWRSnnvkiBcy7AkvJtNycwH0' \
  -H 'Content-Type: application/json' \
  -d '{
  "currency": 397,
  "threshold": 3.69
}'
```

### Последние загруженные котировки

Для неавторизованного пользователя отдает весь список валют, для авторизованного - по его списку отслеживаемых.
Поддерживается сортировка по value. 

Имеет два уровня кеша:
- для полного списка валют (одинаков для всех пользователей);
- для ответа api на конкретный запрос, с разделением по пользователям;

Кеш учитывает параметры запроса.
Кеш сбрасывается при обновлении данных (вручную или по расписанию)

```
GET http://localhost:8000/api/v1/rates/
```

```
curl -X 'GET' \
  'http://localhost:8000/api/v1/rates/?order_by=value' \
  -H 'accept: application/json' \
  -H 'Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk0MDU2NjM4LCJpYXQiOjE2OTQwNTQ4MzgsImp0aSI6IjY2MzUxMjIxNThkZjQ4MmM4NzkwOGUwODUwMGZhZjcxIiwidXNlcl9pZCI6MX0.pwElSZs5G1hOAvsvQb1iWRSnnvkiBcy7AkvJtNycwH0'
```

Ответ:
```
[
  {
    "id": 397,
    "date": "2023-08-26",
    "charcode": "HKD",
    "value": 12.0975
  },
  {
    "id": 395,
    "date": "2023-08-18",
    "charcode": "HUF",
    "value": 26.294
  },
  {
    "id": 400,
    "date": "2023-09-07",
    "charcode": "AED",
    "value": 26.6387
  },
  {
    "id": 398,
    "date": "2023-08-22",
    "charcode": "GEL",
    "value": 35.9062
  }
]
```

### Эндпоинт аналитики

Требует авторизацию. Поддерживает фильтрацию по дате начала и конца выборки.

- добавлено строковое поле, отображающее превышение/равенство/недобор котировки к ПЗ;
- добавлено поле с проценным отношением котировки к ПЗ;
- добавлены флаги, явлется ли конкретная котировка максимальной или минимальной в выборке;

```
GET http://localhost:8000/api/v1/currency/{id}/analytics/
```

```
curl -X 'GET' \
  'http://localhost:8000/api/v1/currency/400/analytics/?date_from=2023-09-01&date_to=2023-09-06&threshold=26.45' \
  -H 'accept: application/json' \
  -H 'Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk0MDU2NjM4LCJpYXQiOjE2OTQwNTQ4MzgsImp0aSI6IjY2MzUxMjIxNThkZjQ4MmM4NzkwOGUwODUwMGZhZjcxIiwidXNlcl9pZCI6MX0.pwElSZs5G1hOAvsvQb1iWRSnnvkiBcy7AkvJtNycwH0'```
```

Ответ:
```
[
  {
    "id": 400,
    "date": "2023-09-06",
    "charcode": "AED",
    "value": 26.5555,
    "is_max_value": true,
    "is_min_value": false,
    "threshold_match_type": "exceeded",
    "percentage_ratio": "100.40"
  },
  {
    "id": 400,
    "date": "2023-09-05",
    "charcode": "AED",
    "value": 26.3054,
    "is_max_value": false,
    "is_min_value": false,
    "threshold_match_type": "less",
    "percentage_ratio": "99.45"
  },
  {
    "id": 400,
    "date": "2023-09-02",
    "charcode": "AED",
    "value": 26.2295,
    "is_max_value": false,
    "is_min_value": false,
    "threshold_match_type": "less",
    "percentage_ratio": "99.17"
  },
  {
    "id": 400,
    "date": "2023-09-01",
    "charcode": "AED",
    "value": 26.2277,
    "is_max_value": false,
    "is_min_value": true,
    "threshold_match_type": "less",
    "percentage_ratio": "99.16"
  }
]
```

## Команда для загрузки данных:

```
make bash
python manage.py load_price_history 
```

```
usage: manage.py load_price_history [-d [DAYS]] [-f [FORCE_EMAILS]]

Загружает историю цен всех котируемых валют.

options:
  -d [DAYS], --days [DAYS]
                        Количество дней, для которых загрузить котировки.
                        
  -f [FORCE_EMAILS], --force_emails [FORCE_EMAILS]
                        Принудительно отправить имейлы, даже если они
                        сегодня уже отправлялись.

```

# Отправка имейл-сообщений с квотами, превзошедшими ПЗ пользователя

Осуществялется через celery-задачу.

Отправка происходит в двух местах:
- при ежедневном обновлении квот;
- при загрузке истории квот через management-команду;

Сообщения отправляются только тем пользователям, чьи ПЗ по валютам были превышены;

Сообщения отправляются не более раза в сутки (это можно обойти в management-команде
с помощью ключа --force_emails - полезно при проверке функционала).

В сообщении присутствует таблица отслеживаемых валют, у которых превышены ПЗ. 
Пример сообщения:

[IMG]

# Механизм работы с кешом

В качестве бэкенда для кеша используется redis.

Данные по последним котировкам всех валют было решено закешировать полностью. Предпосылки: 
- объем данных довольно небольшой (по одной записи на валюту);
- на этой выборке строится ответ по отслеживаемым валютам для каждого пользователя;
Также для каждого пользователя кешируется ответ api по отслеживаемым валютам.

Оба кеша сбрасываются при получении новых котировок (по расписанию или через команду).

Кеш браузера отключен полностью через middleware - это нужно для удобной работы со swagger-ui.
Отключение кеша браузера решает проблему по следующему кейсу:

```
1. Авторизуемся первым пользователем.
2. Дергаем api с данными по отслеживаемым квотам.
3. Браузер кеширует ответ api.
4. Авторизуемся вторым пользователем.
5. Дергаем ту же api с теми же параметрами.
6. Браузер думает, что если api и параметры те же, то нужно отдать закешированные данные. Но эти данные нам не подходят - они для другого пользователя.
```
Актуально только для swagger-ui, в Postman данная проблема отсутсвует по определению.

# Что было сделано по заданию.

Все обязательные и дополнительные пункты, кроме тестов.


# Что можно улучшить:
- management-команду для загрузки истории цен можно продублировать кнопкой в админку;
- добавить в админку настройки переодических задач через библиотеку django-celery-beat;
- разрешить обновление ПЗ в эндпоинте /user-currency/. Либо через метод PUT, либо сделать обработку этого случая в имеющемся методе POST. 
