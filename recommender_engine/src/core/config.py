from dataclasses import dataclass


@dataclass
class Config:
    user_features: bool = False
    num_threads: int = 4
    pg_host: str = "localhost"
    pg_database: str = "movies_database"
    pg_user: str = "postgres"
    pg_password: str = "pass"
