from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import sessionmaker, Session
import pdb

import models 
#from models import SeqInfoNCBIinhouse,SeqInfoNCBIonline,SeqInfoLTTdeep
for mapper in models.Base.registry.mappers:
    print(mapper.class_.__name__)
    
# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL) #, echo=True) #(turn off echo, gets annoying)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

query = (
    select(models.NCBIunreleased,models.DiscreteInfo)
    .join(
        models.DiscreteInfo,
        models.NCBIunreleased.bottleID.ilike(DiscreteInfo.bottleID)
    )
    )

matches = session.execute(diagnostic_query).all()
print(f"Found {len(matches)} matches using case-insensitive search.")
    
# one = 'SAMN52634710'

# #SELECT ... WHERE ...
# #SELECT ... JOIN ... tells how the two tables relate
# query = select(models.SeqInfoLTTdeep).join(models.DiscreteInfo,models.SeqInfoLTTdeep.bottleID == models.DiscreteInfo.bottleID)

# query = select(models.DiscreteInfo).join(models.SeqInfoNCBIinhouse, models.SeqInfoNCBIinhouse.bottleID == models.DiscreteInfo.bottleID)

    
# result = session.execute(query).scalars().first()
# pdb.set_trace()


# # query = select(SeqInfoNCBIonline).where(SeqInfoNCBIonline.biosample == one)

# if result:
#     print(f"Success! Found record ID: {result.id}")
#     # Because of your mapping, you can also easily access its parent metadata:
#     if result.parent_ncbi:
#         print(f"Associated Cruise: {result.parent_ncbi.cruise5}")
# else:
#     print(f"Biosample {one} was not found in the online table.")

# #with Session() as session:
# # 1. Build the query
# query = (
#     select(SeqInfoNCBIonline.biosample)
#     .outerjoin(
#         SeqInfoNCBIinhouse, 
#         SeqInfoNCBIonline.biosample == SeqInfoNCBIinhouse.biosample
#     )
#     .where(SeqInfoNCBIinhouse.biosample == None) # Filter for missing rows
# )

# # 2. Execute and get the single count scalar
# #missing_count = session.execute(query).scalar()
# # Returns a list of SeqInfoNCBIinhouse objects that need to be uploaded
# # 
# rows = session.execute(query).scalars().all()

# pdb.set_trace()

# missing_records = session.execute(query).scalars().all()
    
#print(f"There are {missing_count} biosamples inhouse that are missing online.")


# #how to execute a query
# stmt = select(users)
# with engine.connect() as conn:
#     #pdb.set_trace()
#     rows = session.execute(stmt).all()
#     table_data = [row._mapping for row in rows]
#     df = pd.DataFrame(table_data)
#     #need to reorder the columns for this project, easier to read
#     df = df.reindex(columns = ['cruise','yyyymmdd','bottleID','sType','location','status','extracted','analyst1','V1V2data','V4_16Sdata','V4_18Sdata','mtabData','mtabDataUntargeted'])