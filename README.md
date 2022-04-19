# hw04_tests
Покрытие тестами проекта Yatube

Тренировка написания тестов на Unittest
Как запустить проект: Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/sat0304/api_yamdb.git cd api_yamdb Cоздать и активировать виртуальное окружение:

python3 -m venv venv source venv/bin/activate Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip pip install -r requirements.txt

Создать базу данных из CSV файлов, находящихся в папке STATIC при помощи команды:

python3 manage.py csv_to_sqlite

Выполнить миграции:

python3 manage.py migrate Запустить проект:

python3 manage.py runserver
