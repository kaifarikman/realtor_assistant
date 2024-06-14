from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import config

engine = create_engine(config.DB_CONNECTION_URL, echo=True)
Base = declarative_base()


def create_tables():
    Base.metadata.create_all(bind=engine)
