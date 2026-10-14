from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base  # либо from app.database, в зависимости от импортов

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    description = Column(Text)
    status = Column(String, default="На рассмотрении")