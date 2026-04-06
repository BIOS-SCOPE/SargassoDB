from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///../test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
# delete_db()

#engine = create_engine(SQLALCHEMY_DATABASE_URL,echo=True)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session factory
Session = sessionmaker(bind=engine)

# create a declarative base
Base = declarative_base()

#Can I put this here?
# create the database tables
#Base.metadata.create_all(engine)
