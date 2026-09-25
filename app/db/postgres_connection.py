import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import dbname,user,password,port

def create_db():
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host='localhost',
        port=port
    )
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("CREATE USER app_user WITH PASSWORD 'strong_password';")
            cursor.execute("CREATE DATABASE links OWNER app_user;")

    except Exception as _ex:
        print('Connection error', _ex)
    finally:
        if conn:
            conn.close()

def append_new_db(csv_file):
    conn = psycopg2.connect(
        dbname="app_db",
        user="app_user",
        password="strong_password",
        host="localhost",
        port=5432
    )
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE links(
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    rubrics TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            try:
                import csv
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for row in csv_reader:
                    cursor.execute(
                        "INSERT INTO links (text, rubrics, created_date) VALUES (%s, %s, %s)",
                        (row[0], row[1], row[2])
                        )
            except Exception as _ex:
                print('File reading error')
            finally:
                csv_file.close()
    except Exception as _ex:
        print('Connection error', _ex)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
   ...