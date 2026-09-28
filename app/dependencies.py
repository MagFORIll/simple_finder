from app.services.document_service import DocumentService


_service: DocumentService | None = None


def set_document_service(service: DocumentService) -> None:
    global _service
    _service = service


def get_document_service() -> DocumentService:
    if _service is None:
        raise RuntimeError("Document service has not been initialized")

    return _service
