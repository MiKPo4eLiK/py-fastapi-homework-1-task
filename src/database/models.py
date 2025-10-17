import datetime
from sqlalchemy import (
    String,
    Float,
    Text,
    DECIMAL,
    UniqueConstraint,
    Date,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
)


class Base(DeclarativeBase):
    pass


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    genre: Mapped[str] = mapped_column(String(255), nullable=False)
    overview: Mapped[str] = mapped_column(Text, nullable=False)
    crew: Mapped[str] = mapped_column(Text, nullable=False)
    orig_title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    orig_lang: Mapped[str] = mapped_column(String(50), nullable=False)
    budget: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    country: Mapped[str] = mapped_column(String(3), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "date", name="unique_movie_constraint"),
    )

    def __repr__(self) -> str:
        return f"<Movie(name='{self.name}', release_date='{self.date}', score={self.score})>"
