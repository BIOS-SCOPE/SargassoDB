import pandas as pd
import os
import pdb
from ftplib import FTP
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import update,select
from datetime import datetime

'''
Use this script to check that the sequence matches I am expecting were found
Krista Longnecker 8 April 2026

'''

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session factory
Session = sessionmaker(bind=engine)

# create a declarative base
Base = declarative_base()

# from sqlalchemy import inspect
# inspector = inspect(engine)
# print(inspector.get_table_names())


from sqlalchemy import create_engine, inspect, MetaData, Table
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)

#reflect the tables so I can work on them
user_seqV4_16S = Table('sequencingV4_16S', metadata_obj, autoload_with=engine)
user_seqV4_18S = Table('sequencingV4_18S', metadata_obj, autoload_with=engine)
user_seqV1V2 = Table('sequencingV1V2', metadata_obj, autoload_with=engine)
user_cy = Table('cyverse',metadata_obj,autoload_with=engine)
user_discrete = Table('discrete',metadata_obj,autoload_with=engine)
user_mtab = Table('metabolites',metadata_obj,autoload_with=engine)
user_mtabUntargeted = Table('metabolitesUntargeted',metadata_obj,autoload_with=engine)

# create a session factory
Session = sessionmaker(bind=engine)
session = Session()

#session.query(user_discrete).all()

# from sqlalchemy import inspect
# mapper = inspect(user_discrete)
# column_names = [column.key for column in mapper.columns]
# print(column_names)
# session.query(user_discrete).all()

#query and update
from sqlalchemy import update,select
print('working on V4_16S data')

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_discrete.c.bottleID)
    .where(user_discrete.c.V4_16Sdata == user_cy.c.filename)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
#stmt = update(user_cy).values(source=scalar_subq)
stmt = update(user_cy).values(V4_16S_found=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()  


#is it possible Luis did not find any of the V4_18S files? OR this is a match issue?
from sqlalchemy import update,select #reimport is not necessary but helps me track the sections
print('working on V4_18S data')

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_discrete.c.bottleID)
    .where(user_discrete.c.V4_18Sdata == user_cy.c.filename)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
#stmt = update(user_cy).values(source=scalar_subq)
stmt = update(user_cy).values(V4_18S_found=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()  



#updating...
from sqlalchemy import update,select
print('working on V1V2 data')

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_discrete.c.bottleID)
    .where(user_discrete.c.V1V2data == user_cy.c.filename)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
#stmt = update(user_cy).values(source=scalar_subq)
stmt = update(user_cy).values(V1V2_found=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()  


# see if this worked
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()
users = Table('cyverse', metadata,
    Column('id', Integer, primary_key=True),
    Column('filename', String),
    Column('source', String),
    Column('V4_16S_found', String),
    Column('V4_18S_found', String),
    Column('V1V2_found', String)              
)

#how to execute a query
stmt = select(users)
with engine.connect() as conn:
    rows = session.execute(stmt).all()
    table_data = [row._mapping for row in rows]
    df = pd.DataFrame(table_data)
    df = df.reindex(columns = ['filename','source','V4_16S_found','V4_18S_found','V1V2_found'])

df.head()
df.to_csv('test_data/BIOSSCOPE_checkMatch.csv')


# In[ ]:




