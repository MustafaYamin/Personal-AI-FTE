"""Generic pagination reused by every list endpoint. Keeps limits sane at
10k-user scale — nobody can accidentally request an unbounded result set."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


def page_params(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> PageParams:
    return PageParams(page=page, page_size=page_size)


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


async def paginate(db: AsyncSession, stmt: Select, params: PageParams, schema: type[BaseModel]) -> Page:
    count_stmt = stmt.with_only_columns(func.count()).order_by(None)
    total = (await db.execute(count_stmt)).scalar_one()

    result = await db.execute(stmt.offset((params.page - 1) * params.page_size).limit(params.page_size))
    rows = result.scalars().all()

    total_pages = (total + params.page_size - 1) // params.page_size if total else 0
    return Page(
        items=[schema.model_validate(row) for row in rows],
        page=params.page,
        page_size=params.page_size,
        total=total,
        total_pages=total_pages,
    )
