"""Dependencies for API."""

from fastapi import Query


class PaginationParams:
    """Pagination parameters for endpoints."""

    def __init__(
        self,
        page_number: int = Query(default=1, ge=1),
        page_size: int = Query(default=50, ge=1, le=100),
    ):
        self.page_number = page_number
        self.page_size = page_size
