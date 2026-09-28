from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Document
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_search_returns_newest_20_documents():
    session = AsyncMock()

    documents = [
        Document(
            id=2,
            rubrics=[],
            text="new",
            created_date=datetime(2025, 1, 2),
        ),
        Document(
            id=1,
            rubrics=[],
            text="old",
            created_date=datetime(2025, 1, 1),
        ),
    ]

    scalars = MagicMock()
    scalars.all.return_value = documents

    result = MagicMock()
    result.scalars.return_value = scalars

    session.execute.return_value = result

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(
        return_value=session
    )
    session_factory.return_value.__aexit__ = AsyncMock(
        return_value=None
    )

    index = MagicMock()
    index.search_ids = AsyncMock(return_value=[1, 2])

    service = DocumentService(
        session_factory=session_factory,
        search_index=index,
    )

    result = await service.search("hello")

    assert len(result) == 2
    index.search_ids.assert_awaited_once_with("hello")
