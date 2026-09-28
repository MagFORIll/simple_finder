import ast
import asyncio
import csv
import logging
import os
from datetime import datetime

from app.db.models import Document
from app.db.postgres_connection import initialize_database
from app.index.elastic import create_elasticsearch_client


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


CSV_FILE = os.path.join(
    os.path.dirname(__file__),
    "posts.csv",
)

INDEX_NAME = "documents"


def parse_created_date(value: str) -> datetime:
    return datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S",
    )


def parse_rubrics(value: str) -> list[str]:
    value = value.strip()

    if not value:
        return []

    result = ast.literal_eval(value)

    if not isinstance(result, list):
        raise ValueError("rubricks is not a list")

    return [str(item) for item in result]


def parse_row(row: list[str]) -> Document:

    if len(row) < 3:
        raise ValueError("not enough columns")

    text = row[0].strip()
    created_at = row[1].strip()
    rubricks = row[2].strip()

    if not text:
        raise ValueError("text is empty")

    return Document(
        text=text,
        created_date=parse_created_date(created_at),
        rubrics=parse_rubrics(rubricks),
    )


async def import_data():
    engine, session_factory = await initialize_database()

    elasticsearch_client = create_elasticsearch_client()

    session = session_factory()

    imported_count = 0
    skipped_count = 0

    try:
        if not os.path.exists(CSV_FILE):
            logger.error(
                "CSV file not found: %s",
                CSV_FILE,
            )
            return

        logger.info(
            "Starting import from %s",
            CSV_FILE,
        )

        if not await elasticsearch_client.indices.exists(
            index=INDEX_NAME
        ):
            await elasticsearch_client.indices.create(
                index=INDEX_NAME,
                mappings={
                    "properties": {
                        "id": {
                            "type": "integer"
                        },
                        "text": {
                            "type": "text"
                        },
                    }
                },
            )

            logger.info(
                "Created Elasticsearch index '%s'",
                INDEX_NAME,
            )

        with open(
            CSV_FILE,
            "r",
            encoding="utf-8",
            newline="",
        ) as csv_file:

            reader = csv.reader(csv_file)


            next(reader, None)

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                try:
                    document = parse_row(row)


                    session.add(document)


                    await session.flush()

                    document_id = document.id


                    await elasticsearch_client.index(
                        index=INDEX_NAME,
                        id=str(document_id),
                        document={
                            "id": document_id,
                            "text": document.text,
                        },
                    )

                    imported_count += 1

                except Exception as error:
                    skipped_count += 1

                    logger.warning(
                        "Skipping row %s: %s",
                        row_number,
                        error,
                    )


            await session.commit()

        await elasticsearch_client.indices.refresh(
            index=INDEX_NAME
        )

        logger.info(
            "Import finished. Imported: %s, skipped: %s",
            imported_count,
            skipped_count,
        )

    except Exception:
        await session.rollback()
        raise

    finally:
        await session.close()
        await elasticsearch_client.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(import_data())
