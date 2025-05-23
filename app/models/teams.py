from sqlalchemy import Column, String
from app.db import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
