#working.py
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import update,select
import pandas as pd
import os
import pdb #use with pdb.set_trace()

#import database #cannot get this to work, skip for now
# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session factory
Session = sessionmaker(bind=engine)


#reflect the tables so I can work on them
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)

user_seqV4_16S = Table('sequencingV4_16S', metadata_obj, autoload_with=engine)
user_seqV4_18S = Table('sequencingV4_18S', metadata_obj, autoload_with=engine)
user_seqV1V2 = Table('sequencingV1V2', metadata_obj, autoload_with=engine)
user_discrete = Table('discrete',metadata_obj,autoload_with=engine)
user_mtab = Table('metabolites',metadata_obj,autoload_with=engine)
user_mtabUntargeted = Table('metabolitesUntargeted',metadata_obj,autoload_with=engine)
user_cy = Table('cyverse',metadata_obj,autoload_with=engine) 
user_basics = Table('sequencingBasics',metadata_obj,autoload_with=engine)

with Session(engine) as session:
    # Get one NewID from the master table
    pdb.set_trace()
    bottle = session.get(DiscreteInfo, 1) 
    
    print(f"Bottle ID: {bottle.bottleID}")
    print(f"Depth: {bottle.nominalDepth}")
    
    # 2. Instantly loop through all sequencing runs linked to this bottle!
    # (SQLAlchemy automatically handles the database join behind the scenes)
    for run in bottle.v4_16s_runs:
        print(f" -> Found Sequence File: {run.filename}")
        print(f" -> V4 16S Data: {run.V4_16Sdata}")
