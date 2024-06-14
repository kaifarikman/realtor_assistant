from bot.db.db import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    status = Column(Integer)
    days = Column(Integer)
    trial_status = Column(Integer)
