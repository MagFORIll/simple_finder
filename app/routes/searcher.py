from fastapi import APIRouter, HTTPException, Query

from app.dependencies import get_document_service
from app.schemas import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get(
    "/search",
    response_model=list[DocumentResponse],
    summary="Search documents",
)
async def search_documents(
    query: str = Query(
        min_length=1,
        description="Arbitrary text search query",
    ),
):
    service = get_document_service()

    return await service.search(query)


@router.delete(
    "/{document_id}",
    status_code=204,
    summary="Delete a document",
)
async def delete_document(document_id: int):
    service = get_document_service()

    deleted = await service.delete(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )
