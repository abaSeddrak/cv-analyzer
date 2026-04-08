from sqlalchemy import Column, Integer, String
from database import Base

class CV(Base):
    __tablename__ = "cv_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    city = Column(String)