Зависимости
pip install -r requirements.txt

Создание PostgreSQL на macOS (Последние три команды отвечают за права)
    psql postgres
    CREATE DATABASE questions_db;
    \c questions_db;
    ALTER SCHEMA public OWNER TO postgres;
    GRANT CREATE ON SCHEMA public TO postgres;
    GRANT CREATE ON SCHEMA public TO PUBLIC;


Миграции
python manage.py makemigrations
python manage.py migrate

Создание суперпользователя
python manage.py createsuperuser

Заполнение БД
python manage.py fill_db 10

Запуск сайта
python manage.py runserver
