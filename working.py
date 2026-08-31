#working.py
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
#from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from models import DiscreteInfo, SeqInfoBasics #here I can just use SeqInfoBasics
#import models #if I use this, then syntax is models.SeqInfo
#from models import Base,SeqInfoV4 #here I can just use SeqInfo

'''
working
Krista Longnecker 30 August 2026

'''

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL) #, echo=True) #(turn off echo, gets annoying)

# # create a session factory
# Session = sessionmaker(bind=engine)

# #create the database
# models.Base.metadata.create_all(engine)


with Session(engine) as session:
    # 1. Build a SELECT statement that joins 'discrete' to 'sequencingBasics'
    stmt = (
        select(DiscreteInfo, SeqInfoBasics)
        .join(SeqInfoBasics, DiscreteInfo.bottleID == SeqInfoBasics.bottleID)
    )
    
    # 2. Execute the join query
    result = session.execute(stmt).all()
    
    table_data = []
    for disc, seq in result:
        table_data.append({
            "Bottle ID": disc.bottleID,
            "Cruise": disc.cruise,
            "Extracted Code": seq.extracted if seq else None,
            "Analyst": seq.analyst1 if seq else None
        })
        
    df = pd.DataFrame(table_data)
    


print(df.head())
# df.to_csv('test_data/out1.csv') 

# In Jupyter, just typing 'df' will print a gorgeous HTML table grid
print(df.to_string(index=False)) 




