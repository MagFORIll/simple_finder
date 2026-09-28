from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.db.models import Document
from app.index.elastic import ElasticsearchIndex


class DocumentService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        search_index: ElasticsearchIndex,
    ):
        self.session_factory = session_factory
        self.search_index = search_index

    async def search(
        self,
        query: str,
    ) -> list[Document]:

        ids = await self.search_index.search_ids(query)

        if not ids:
            return []


        async with self.session_factory() as session:
            statement = (
                select(Document)
                .where(Document.id.in_(ids))
                .order_by(Document.created_date.desc())
                .limit(20)
            )

            result = await session.execute(statement)

            return list(result.scalars().all())

    async def delete(
        self,
        document_id: int,
    ) -> bool:
        async with self.session_factory() as session:

            document = await session.get(
                Document,
                document_id,
            )

            if document is None:
                return False

            document_text = document.text


            await self.search_index.delete_document(
                document_id
            )

            try:

                await session.execute(
                    delete(Document).where(
                        Document.id == document_id
                    )
                )

                await session.commit()

            except Exception:
                await self.search_index.index_document(
                    document_id,
                    document_text,
                )

                raise

            return True
