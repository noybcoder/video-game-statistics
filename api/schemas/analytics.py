from pydantic import BaseModel

class PlatformYearCount(BaseModel):
    platform: str
    release_year: int
    game_count: int

class GenreCount(BaseModel):
    genre: str
    game_count: int

class DeveloperGenre(BaseModel):
    developer: str
    genre: str
    total_game_count: int
    pct_of_total_game_count: float

class EngineCount(BaseModel):
    engine: str
    game_count: int
    developer_count: int

class GenreRanking(BaseModel):
    genre: str
    release_year: int
    weighted_average_rating: float