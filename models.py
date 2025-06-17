from sqlalchemy import Column, String, DateTime, JSON
from db import Base

class UserPing(Base):
    __tablename__ = "user_pings"

    user = Column(String, primary_key=True)
    timestamp = Column(DateTime)
    location = Column(JSON)
