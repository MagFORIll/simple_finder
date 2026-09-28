# Simple Finder

Простой HTTP-сервис полнотекстового поиска документов.

## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Elasticsearch
- Docker Compose
- pytest

## Структура

```text
app/
├── db/
│   ├── models.py
│   └── postgres_connection.py
├── index/
│   └── elastic.py
├── routes/
│   └── searcher.py
├── services/
│   └── document_service.py
├── scripts/
│   └── import_data.py
├── config.py
├── dependencies.py
├── schemas.py
└── main.py

tests/
├── unit/
└── functional/
```

## Запуск через Docker

Запустить инфраструктуру:

```bash
docker compose up --build
```

API будет доступно на:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

OpenAPI:

```text
http://localhost:8000/openapi.json
```

## Импорт CSV

Файл:

```text
app/scripts/posts.csv
```
```bash
docker compose exec app python -m app.scripts.import_data
```


Пример:

```csv
rubrics,text,created_date
"['news','sport']","Some document text","2019-09-01 09:48:41"
```

Запуск импорта локально:

```bash
python -m app.scripts.import_data
```

Для Docker можно запустить импорт внутри контейнера:

```bash
docker compose exec app python -m app.scripts.import_data
```

## API

### Search

```http
GET /documents/search?query=python
```

Сервис:

1. отправляет запрос в Elasticsearch;
2. получает IDs документов;
3. загружает полные документы из PostgreSQL;
4. сортирует их по `created_date` по убыванию;
5. возвращает первые 20.

Ответ:

```json
[
  {
    "id": 123,
    "rubrics": ["news"],
    "text": "Document text",
    "created_date": "2019-09-01T09:48:41"
  }
]
```

### Delete

```http
DELETE /documents/123
```

Если документа нет:

```http
404
```

Если удаление успешно:

```http
204
```

Удаление выполняется из PostgreSQL и Elasticsearch.

## Тесты

```bash
pytest
```

## Архитектура

PostgreSQL является источником полных данных.

Elasticsearch хранит только:

```text
id
text
```

Поэтому сортировка по `created_date` выполняется в PostgreSQL.

При поиске сервис получает все подходящие IDs из Elasticsearch, затем PostgreSQL возвращает максимум 20 документов, отсортированных по дате создания.

## Инициализация PostgreSQL

При первом запуске приложение:

1. подключается к системной БД `postgres`;
2. создаёт `app_user`, если его нет;
3. создаёт `app_db`, если её нет;
4. создаёт таблицу `documents`.

При последующих запусках существующие объекты не пересоздаются.
