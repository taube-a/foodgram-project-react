![Workflow status](https://github.com/taube-a/foodgram-project-react/actions/workflows/foodgram-proeject-react_workflow.yml/badge.svg)

# Дипломный проект "Продуктовый помощник"

Проект развёрнут по ip-адресу [158.160.29.172](http://158.160.29.172)

## Описание проекта

«Продуктовый помощник» - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Используемые технологии

+ Python 
+ Django
+ PostgreSQL
+ rest_api
+ Docker
+ Yandex.Cloud

Полный перечень библиотек расположен в репозитории по адресу backend/requirements.txt

## Установка и запуск

### A. На локальной машине

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/taube-a/foodgram-project-react.git

cd foodgram-project-react
```

2. Перейти в папку infra.

3. Создать файл .env с переменными окружения (см. пример в файле example.env). 

4.  1. В файл docker-compose.yml внести следующие изменения:

        Заменить строки 
        ```
        image: taubeau/foodgram_backend:latest
        ```
        и
        ```
        image: taubeau/foodgram_frontend:latest
        ```
        на
        ```
        build: ../backend/
        ```
        и
        ```
        build: ../frontend/
        ```
        соответсвенно.
    
    2. В файл nginx.conf внести следующие изменения:

        Заменить строку
        ```
        server_name 158.160.29.172;
        ```
        на
        ```
        server_name 127.0.0.1;
        ```

5. Остановить и (при необходимости) удалить все запущенные Докер-контейнеры:
```
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)
```

6. Запустить сборку и запуск контейнеров приложения:
```
sudo docker-compose up -d --build
```

7. Выполнить и применить миграции, наполнить базу данных, загрузить статику:
```
sudo docker-compose exec -T backend python manage.py makemigrations
sudo docker-compose exec -T backend python manage.py migrate
sudo docker-compose exec -T backend python manage.py loaddata ./data/foodgram_db.json
sudo docker-compose exec -T backend python manage.py collectstatic --no-input
```

8.  Сервер запущен по адресу: 127.0.0.1


### B. На сервере

1. В корневую папку дублируйте следующие файлы из данного репозитория

Из *infra/*:

+ docker-compose.yml
+ nginx.conf
    Позже в них будут внесены изменения для настройки проекта на Вашем сервере

Из *backend/data*:

+ foodgram_db.json

    **!** Демо база данных для скачивания необязательна.

3. Создать файл .env с переменными окружения (см. пример в файле example.env). 

4.  В файл nginx.conf внести следующие изменения:

Заменить строку
        
```
server_name 158.160.29.172;
```
на
```
server_name вставить.ip.вашего.сервера;
```

5. Установить на сервер Docker:
```
sudo apt install docker.io 
```

6. Установить docker-compose на сервере:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

7. Остановить и (при необходимости) очистить все запущенные Докер-контейнеры:
```
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)
```

8. Скачать образы бекэнда и фронтэнда на сервер:
```
sudo docker pull taubeau/foodgram_backend:latest
sudo docker pull taubeau/foodgram_frontend:latest
```

9. Запустить сборку и запуск контейнеров приложения:
```
sudo docker-compose up -d --build
```

10. Выполнить и применить миграции, загрузить статику:
```
sudo docker-compose exec -T backend python manage.py makemigrations
sudo docker-compose exec -T backend python manage.py migrate
sudo docker-compose exec -T backend python manage.py collectstatic --no-input
```

11. При необходимости скопировать в контейнер и загрузить данные для базы данных:
```
sudo docker ps 
# В появившейся таблице скопировать CONTAINER ID контейнера бекэнда. Далее для примера это будет f93c59f7e7a8
sudo docker cp foodgram_db.json f93c59f7e7a8:app/data
sudo docker-compose exec backend python manage.py loaddata ./data/foodgram_db.json
```

**!** Данные от учётной пользователя администратора: 

 ```
    email: admin@admin.com
    password: admin
```

12.  Сервер запущен по адресу Вашего сервера.


Автор: [Анастасия Таубе](https://github.com/taube-a)