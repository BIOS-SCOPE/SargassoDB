from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import update,select
import pandas as pd
import os
import pdb #use with pdb.set_trace()

'''
Now I need to update the database based on the links across tables in 
the database
And, because I had to look this up, crud is:
CREATE
READ
UPDATE
DELETE
Krista Longnecker, 6 April 2026
Krista Longnecker, 27 June 2026
'''


#import database #cannot get this to work, skip for now
# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session factory
SessionLocal = sessionmaker(bind=engine)


#reflect the tables so I can work on them
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)

user_seqV4_16S = Table('seqV4_16S', metadata_obj, autoload_with=engine)
user_seqV4_18S = Table('seqV4_18S', metadata_obj, autoload_with=engine)
user_seqV1V2 = Table('seqV1V2', metadata_obj, autoload_with=engine)
user_discrete = Table('discrete',metadata_obj,autoload_with=engine)
user_mtab = Table('metabolites',metadata_obj,autoload_with=engine)
user_mtabUntargeted = Table('metabolitesUntargeted',metadata_obj,autoload_with=engine)
user_cy = Table('cyverse',metadata_obj,autoload_with=engine) 
user_basics = Table('seqBasics',metadata_obj,autoload_with=engine)


#pdb.set_trace()
#
#see all of what is in table (leave query here for future reference, not in use)
#session.query(SeqInfoV4).all()

# pull in the data re: general sequencing information
## pull in the data re: general sequencing information
print('Pull in the basic sequencing information')
# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_basics.c.extracted)
    .where(user_discrete.c.bottleID == user_basics.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

#This will break because I am no longer pre-filling discrete with empty columns
#leave a stop here in case I try this again
print("I know this will break, see comment in crud.py")
pdb.set_trace()
    
# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(extracted=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
    
# link the V1V2 data
# link the V1V2 data
print('linking the V1V2 data')
    
# create a session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_seqV1V2.c.filename)
    .where(user_discrete.c.bottleID == user_seqV1V2.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(V1V2data=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
   

# link the V4_16S
# link the V4_16S
print('linking the V4_16S data')

# create a session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_seqV4_16S.c.filename)
    .where(user_discrete.c.bottleID == user_seqV4_16S.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(V4_16Sdata=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()   
    
#link the V4_18S
#link the V4_18S
print('linking the V4_18S data')

# create a session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

#see all of what is in table (leave query here for future reference, not in use)
#session.query(SeqInfoV4).all()

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_seqV4_18S.c.filename)
    .where(user_discrete.c.bottleID == user_seqV4_18S.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(V4_18Sdata=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()       
        
 
#finally the metabolite data
#finally the metabolite data
print('linking the metabolite data')

# create a session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_mtab.c.dataSource)
    .where(user_discrete.c.bottleID == user_mtab.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(mtabData=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
    

#adding the untargeted metabolite data
#adding the untargeted metabolite data
print('linking the untargeted metabolite data')

# create a session factory
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 1. Define the subquery to fetch a value from the second table
scalar_subq = (
    select(user_mtabUntargeted.c.dataSource)
    .where(user_discrete.c.bottleID == user_mtabUntargeted.c.bottleID)
    .limit(1)
    .scalar_subquery()
)

# 2. Use the subquery in the .values() clause of an update statement
stmt = update(user_discrete).values(mtabDataUntargeted=scalar_subq)

#then execute the statement
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()



    
# see if this worked, export DataFrame if it did
print('check if this all worked')

# Create a session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()
users = Table('discrete', metadata,
    Column('id', Integer, primary_key=True),
    Column('bottleID', String),
    Column('cruise', String),
    Column('yyyymmdd',String),
    Column('sType', String),
    Column('location',String),
    Column('status',String),
    Column('extracted',String),
    Column('analyst1',String),
    Column('V4_16Sdata',String),
    Column('V4_18Sdata',String),
    Column('V1V2data',String),
    Column('mtabData',String),
    Column('mtabDataUntargeted',String)              
)

#how to execute a query
stmt = select(users)
with engine.connect() as conn:
    #pdb.set_trace()
    rows = session.execute(stmt).all()
    table_data = [row._mapping for row in rows]
    df = pd.DataFrame(table_data)
    #need to reorder the columns for this project, easier to read
    df = df.reindex(columns = ['cruise','yyyymmdd','bottleID','sType','location','status','extracted','analyst1','V1V2data','V4_16Sdata','V4_18Sdata','mtabData','mtabDataUntargeted'])

#export the final result as a CSV file
df.to_csv('test_data/BIOSSCOPE_availableData.2026.06.27.csv')    
#df_final = df  



##this is the test without the metabolite data, just leave here in case it is useful later
# # see if this worked
# #Base.metadata.create_all(engine)
# print('check if this all worked (skipping metabolite data')

# # Create a session
# Session = sessionmaker(bind=engine)
# session = Session()

# from sqlalchemy import Table, Column, Integer, String, MetaData

# metadata = MetaData()
# users = Table('discrete', metadata,
    # Column('id', Integer, primary_key=True),
    # Column('bottleID', String),
    # Column('cruise', String),
    # Column('yyyymmdd',String),
    # Column('V4data',String),
    # Column('V1V2data',String),
    # #Column('mtabData',String)
              
# )

# #how to execute a query
# stmt = select(users)
# with engine.connect() as conn:
    # rows = session.execute(stmt).all()
    # table_data = [row._mapping for row in rows]
    # df = pd.DataFrame(table_data)
    # df = df.reindex(columns = ['cruise','yyyymmdd','bottleID','V1V2data','V4data'])#,'mtabData'])
    

# #export the final result as a CSV file
# df.to_csv('test_data/BIOSSCOPE_availableData.2026.04.06.csv')    
# df_final = df    
    

# pdb.set_trace()
# users = session.query(user_seqV1V2).all()
# print(users)

    
