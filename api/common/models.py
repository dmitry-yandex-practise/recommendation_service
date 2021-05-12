from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Recommendations(Base):
    __tablename__ = 'recommendations'
    __table_args__ = {"schema": "recommendations"}

    userId = Column('user_id', Integer, primary_key=True)
    recommendations = Column('recommendations', JSONB)
