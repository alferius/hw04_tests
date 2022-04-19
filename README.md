# hw04_tests
Покрытие тестами проекта Yatube. Тренировка написания тестов на Unittest

Как запустить проект: Клонировать репозиторий и перейти в него в командной строке:
git clone https://github.com/alferius/hw04_tests.git
cd hw04_tests

Cоздать и активировать виртуальное окружение:
python3 -m venv venv source venv/bin/activate 

Установить зависимости из файла requirements.txt:
python3 -m pip install --upgrade pip pip install -r requirements.txt

Выполнить миграции:
python3 manage.py migrate Запустить проект:

python3 manage.py runserver
