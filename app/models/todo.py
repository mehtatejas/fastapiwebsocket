from sqlalchemy import Column, String, Boolean
from app.db import Base

class Todo(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
