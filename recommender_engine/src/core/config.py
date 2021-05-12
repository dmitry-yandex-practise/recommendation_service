from dataclasses import dataclass


@dataclass
class Config:
    user_features: bool = False
