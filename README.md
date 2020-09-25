# foodgram-project
Ip address: http://130.193.39.75/
Данный проект представляет собой итоговую работы для 1 когорты бэкэнд-разработчика yandex.praktikum

## Начало работы

Инструкции ниже описывают запуск проекта

### Подготовка

Прежде чем запустить проект, необходимо установить docker, docker-compose и всё необходимое, находящееся в requirements.txt (команды приведены в ОС Ubunta. NB! В иных ОС действия могут отличаться)

```
sudo apt install docker
sudo apt install docker-compose
sudo pip install -r requirements.txt
```

### Команды для запуска приложения
Используется docker-compose
```
sudo docker-compose up
```

### Настройка проекта
Необходимо подключиться внутрь контейнера:
```
sudo docker exec -it <id контейнера> bash
```
и выполнить там миграции, а так же создать суперпользователя базу:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```
При желании аналогичные действия возможно сделать с помощью команд doker-compose, например:
```
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
```

## Built With

* [Django](https://www.djangoproject.com/) - Веб-фреймворк
* [Docker](https://www.docker.com/) - Контейнер
* [Nginx](https://nginx.org/ru/) - Прокси-сервер для отдачи статики
* [Gunicorn](https://gunicorn.org/) - WSGI-сервер 
* [PostgreSQL](https://www.postgresql.org/) - БД
