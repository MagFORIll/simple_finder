from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine import URL

from app.config import (
    DB_NAME,
    DB_PASSWORD,
    DB_USER,
    POSTGRES_ADMIN_PASSWORD,
    POSTGRES_ADMIN_USER,
    POSTGRES_HOST,
    POSTGRES_PORT,
)
from app.db.models import Base


def build_database_url(
    user: str,
    password: str,
    database: str,
) -> URL:
    return URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=database,
    )


async def create_user_and_database() -> None:

    import asyncpg

    connection = await asyncpg.connect(
        user=POSTGRES_ADMIN_USER,
        password=POSTGRES_ADMIN_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database="postgres",
    )

    try:
        role_exists = await connection.fetchval(
            "SELECT 1 FROM pg_roles WHERE rolname = $1",
            DB_USER,
        )

        if not role_exists:
            escaped_password = DB_PASSWORD.replace("'", "''")

            await connection.execute(
                f'CREATE USER "{DB_USER}" WITH PASSWORD \'{escaped_password}\''
            )

        database_exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            DB_NAME,
        )

        if not database_exists:
            # PostgreSQL does not support a parameter for database name.
            # DB_NAME comes from our controlled environment configuration.
            await connection.execute(
                f'CREATE DATABASE "{DB_NAME}" OWNER "{DB_USER}"'
            )
    finally:
        await connection.close()


def create_engine_and_session() -> tuple[
    AsyncEngine,
    async_sessionmaker[AsyncSession],
]:
    engine = create_async_engine(
        build_database_url(
            DB_USER,
            DB_PASSWORD,
            DB_NAME,
        ),
        pool_pre_ping=True,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    return engine, session_factory


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def initialize_database() -> tuple[
    AsyncEngine,
    async_sessionmaker[AsyncSession],
]:
    await create_user_and_database()

    engine, session_factory = create_engine_and_session()
    await create_tables(engine)

    return engine, session_factory
