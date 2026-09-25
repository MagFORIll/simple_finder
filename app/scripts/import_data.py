import os

def open_csv_file():
    global csv_file
    current_dir = os.path.dirname(__file__)
    try:
        csv_file = open(current_dir + '\\posts.csv', mode='r', newline='',encoding='utf-8')
        return csv_file
    except Exception as _ex:
        print('Open file error:', _ex)


if __name__ == '__main__':
    from app.db.postgres_connection import create_db, append_new_db
    create_db()
    append_new_db(open_csv_file())


