from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database.session import get_db
from src.database.models import MovieModel
from src.schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter(prefix="/theater/movies", tags=["Movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(func.count()).select_from(MovieModel))
    total_items = result.scalar_one()

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = ceil(total_items / per_page)
    offset = (page - 1) * per_page

    result = await db.execute(
        select(MovieModel).order_by(MovieModel.id).offset(offset).limit(per_page)
    )
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    base_url = "/theater/movies/"

    next_page = (
        f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None
    )
    prev_page = (
        f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    )

    return {
        "total": total_items,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "next": next_page,
        "previous": prev_page,
        "items": movies,
    }


@router.get("/{movie_id}", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie
