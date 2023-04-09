![Workflow status](https://github.com/taube-a/foodgram-project-react/actions/workflows/foodgram-proeject-react_workflow.yml/badge.svg)

# Дипломный проект "Продуктовый помощник"
### **Этап 1**: проверка кода проекта (включая файл зависимостей requirements.txt). 

## Описание проекта

«Продуктовый помощник» - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Используемые технологии

+ Python 
+ Django
+ PostgreSQL
+ rest_api

Полный перечень библиотек расположен в репозитории по адресу backend/requirements.txt

## Установка и запуск

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/taube-a/foodgram-project-react.git

cd foodgram-project-react
```

2. Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv        (для Mac/Linux)
source venv/bin/activate    (для Mac/Linux)
```

```
python -m venv venv         (для Windows)
env/Scripts/activate.bat    (для Windows)
```

3. Обновить pip, установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip    (для Mac/Linux)
python -m pip install --upgrade pip     (для Windows)
```
```
pip install -r backend/requirements.txt
```

4. В папке infra создать файл .env с переменными окружения (см. пример в файле example.env):

5. Из папки backend подготовить проект к запуску: 

```
python manage.py migrate
python manage.py loaddata ../data/foodgram_db.json
python manage.py collectstatic --no-input
```

При желании можно создать нового супер пользователя:
```
python manage.py createsuperuser
```

Данные для входа в админку через предустановленного супер-пользовталея: 
```
e-mail: admin@admin.com
password: admin
```


6. Запустить проект: 
```
python manage.py runserver
```

7.  Сервер запущен по адресу: 127.0.0.1:8000


Автор: [Анастасия Таубе](https://github.com/taube-a)