from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError

from app.config import ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX


class ElasticsearchIndex:
    def __init__(
        self,
        client: AsyncElasticsearch,
        index_name: str = ELASTICSEARCH_INDEX,
    ):
        self.client = client
        self.index_name = index_name

    async def ensure_index(self) -> None:
        exists = await self.client.indices.exists(
            index=self.index_name,
        )

        if not exists:
            await self.client.indices.create(
                index=self.index_name,
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "text": {"type": "text"},
                    }
                },
            )

    async def index_document(
        self,
        document_id: int,
        text: str,
    ) -> None:
        await self.client.index(
            index=self.index_name,
            id=str(document_id),
            document={
                "id": str(document_id),
                "text": text,
            },
            refresh="wait_for",
        )

    async def bulk_index(
        self,
        documents: list[tuple[int, str]],
    ) -> None:
        if not documents:
            return

        operations = []

        for document_id, text in documents:
            operations.append(
                {
                    "index": {
                        "_index": self.index_name,
                        "_id": str(document_id),
                    }
                }
            )

            operations.append(
                {
                    "id": str(document_id),
                    "text": text,
                }
            )

        response = await self.client.bulk(
            operations=operations,
            refresh="wait_for",
        )

        if response["errors"]:
            failed = [
                item
                for item in response["items"]
                if item.get("index", {}).get("error")
            ]

            raise RuntimeError(
                f"Elasticsearch bulk indexing failed: {failed[:3]}"
            )

    async def search_ids(
        self,
        query: str,
    ) -> list[int]:

        result_ids: list[int] = []
        search_after = None
        page_size = 1000

        while True:
            body = {
                "query": {
                    "match": {
                        "text": {
                            "query": query,
                        }
                    }
                },
                "sort": [
                    {
                        "id": "asc"
                    }
                ],
                "size": page_size,
            }

            if search_after is not None:
                body["search_after"] = search_after

            response = await self.client.search(
                index=self.index_name,
                **body,
            )

            hits = response["hits"]["hits"]

            if not hits:
                break

            for hit in hits:
                result_ids.append(
                    int(hit["_id"])
                )

            if len(hits) < page_size:
                break

            search_after = hits[-1]["sort"]

        return result_ids

    async def delete_document(
            self,
            document_id: int,
    ) -> None:
        try:
            response = await self.client.delete(
                index=self.index_name,
                id=str(document_id),
                refresh="wait_for",
            )

            if response.get("result") != "deleted":
                raise RuntimeError(
                    f"Failed to delete document {document_id} "
                    f"from Elasticsearch: {response}"
                )

        except NotFoundError:
            return


def create_elasticsearch_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(
        ELASTICSEARCH_HOST,
    )
