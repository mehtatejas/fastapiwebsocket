from sqlalchemy import Column, String
from app.db import Base

class Setting(Base):
    __tablename__ = "settings"
    id = Column(String, primary_key=True, index=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
