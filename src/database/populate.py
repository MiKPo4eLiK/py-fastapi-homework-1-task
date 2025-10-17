import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

from src.config import get_settings
from src.database.models import MovieModel
from src.database.session import (
    get_db_contextmanager,
    init_db,
)


class CSVDatabaseSeeder:
    def __init__(self, csv_file_path: str, db_session: AsyncSession):
        self._csv_file_path = csv_file_path
        self._db_session = db_session

    async def is_db_populated(self) -> bool:
        result = await self._db_session.execute(select(func.count()).select_from(MovieModel))
        total_count = result.scalar_one()
        return total_count > 0

    async def _preprocess_csv(self) -> pd.DataFrame:
        data = pd.read_csv(self._csv_file_path)
        data = data.drop_duplicates(subset=['names', 'date_x'], keep='first')
        data['crew'] = data['crew'].fillna('Unknown')
        data['genre'] = data['genre'].fillna('Unknown')
        data['genre'] = data['genre'].str.replace('\u00A0', '', regex=True)
        data['date_x'] = data['date_x'].str.strip()
        data['date_x'] = pd.to_datetime(data['date_x'], format='%m/%d/%Y', errors='coerce')
        data['date_x'] = data['date_x'].dt.date
        print("Preprocessing csv file")
        return data

    async def seed(self) -> None:
        try:
            if self._db_session.in_transaction():
                await self._db_session.rollback()

            data = await self._preprocess_csv()

            async with self._db_session.begin():
                for _, row in tqdm(data.iterrows(), total=data.shape[0], desc="Seeding database"):
                    budget = int(row['budget_x']) if not pd.isna(row['budget_x']) else 0
                    revenue = int(row['revenue']) if not pd.isna(row['revenue']) else 0

                    movie = MovieModel(
                        name=row['names'],
                        date=row['date_x'],
                        score=float(row['score']),
                        genre=row['genre'],
                        overview=row['overview'],
                        crew=row['crew'],
                        orig_title=row['orig_title'],
                        status=row['status'],
                        orig_lang=row['orig_lang'],
                        budget=budget,
                        revenue=revenue,
                        country=row['country']
                    )
                    self._db_session.add(movie)

        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            await self._db_session.rollback()
            raise


async def main() -> None:
    settings = get_settings()
    await init_db()

    async with get_db_contextmanager() as db_session:
        seeder = CSVDatabaseSeeder(settings.PATH_TO_MOVIES_CSV, db_session)

        if not await seeder.is_db_populated():
            try:
                await seeder.seed()
                print("Database seeding completed successfully.")
            except Exception as e:
                print(f"Failed to seed the database: {e}")
        else:
            print("Database is already populated. Skipping seeding.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
