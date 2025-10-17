from typing import List, Optional
from pydantic import BaseModel
import datetime


# noinspection PyMissingConstructor
class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: datetime.date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: int
    revenue: int
    country: str

    class Config:
        orm_mode = True


# noinspection PyMissingConstructor
class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int
