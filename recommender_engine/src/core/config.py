from dataclasses import dataclass


@dataclass
class Config:
    user_features: bool = False
    num_threads: int = 4
