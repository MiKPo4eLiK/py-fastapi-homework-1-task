from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from src.database import (
    get_db,
    MovieModel,
)
from src.schemas.movies import (
    MovieDetailResponseSchema,
    MovieListResponseSchema,
)


router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=20),
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MovieModel))
    total_items = len(result.scalars().all())

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = ceil(total_items / per_page)
    offset = (page - 1) * per_page

    result = await db.execute(select(MovieModel).offset(offset).limit(per_page))
    movies = result.scalars().all()

    base_url = "/api/v1/theater/movies/"
    prev_page = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items
    }


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_detail(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

    return movie
