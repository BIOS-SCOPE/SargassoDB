import pandas as pd
import os
import pdb #user with set_trace()
from ftplib import FTP
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

import models #if I use this, then syntax is models.SeqInfo
#from models import Base,SeqInfoV4 #here I can just use SeqInfo

import pdb #use with set_trace()

'''
Populate the BIOS-SCOPE database with information, for now just where to 
find the files/databases where the information is located. Later will
probably be links to the actual data
Krista Longnecker 6 April 2026

'''

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///../test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL) #echo=True) (turn off echo, gets annoying)

# create a session factory
Session = sessionmaker(bind=engine)

#create the database
models.Base.metadata.create_all(engine)

##I think (from Stack Overflow) this will empty the database before I start
import contextlib
from sqlalchemy import MetaData

meta = MetaData()

with contextlib.closing(engine.connect()) as con:
    trans = con.begin()
    for table in reversed(meta.sorted_tables):
        con.execute(table.delete())
    trans.commit()

    
# # insert some data, setup functions, one per data type
def load_discrete_info():
    print('Loading discrete sample information')
    data_dir = 'test_data/BIOS-SCOPE time series/'
    fName = 'BATS_BS_COMBINED_MASTER_mini.xlsx' #use mini for testing
    #fName = 'BATS_BS_COMBINED_MASTER_latest.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),sheet_name='DATA'))

    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.DiscreteInfo()
        db.bottleID = row['New_ID'] 
        db.cruise = row['Cruise_ID']
        db.cast = row['Cast']
        db.niskin = row['Niskin']
        db.yyyymmdd = row['yyyymmdd']
        db.nominalDepth = row['Nominal_Depth']
        session.add(db)
    
    session.commit()
    
def load_V4_sequencing_info():
    print('Loading V4 sequencing information')
    data_dir = 'test_data/BIOS-SCOPE time series/'
    fName = 'V4_dada2_read_info_03052026.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName)))
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !

    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV4()
        db.bottleID = row['BottleID'] 
        db.cast = row['Cast']
        db.filename = row['FilenameinCyverse']
        db.V4data = fName
        session.add(db)
    
    session.commit()
    
def load_V1V2_sequencing_info():
    print('Loading V1V2 sequencing information')
    data_dir = 'test_data/BIOS-SCOPE time series/'
    fName = 'V1V2_dada2_read_info_03052026.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),
                                   dtype={'Bottle ID':str,'Cruise':str,'Cast':str,'Depth':str}))
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !
    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV1V2()
        db.bottleID = row['BottleID'] 
        db.cast = row['Cast']
        db.filename = row['FileName']
        db.V1V2data = fName
        session.add(db)
    
    session.commit()

def load_cyverse_info():
    #keep this, but for the moment I am not using the list of files from Luis
    print('Loading sequencing information')
    dataDir = 'test_data/BIOS-SCOPE time series/'
    fName = 'files_shortList.txt'
    df = pd.read_csv(os.path.join(dataDir,fName),sep='\t',header=None,comment = '#')

    #strip off the end of the filename
    for index,row in df.iterrows():
        file = os.path.basename(row.to_string()).strip('.gz')
        df.loc[index,'filename'] = file

    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.CyverseInfo()
        db.filename = row['filename'] 
        session.add(db)
    
    session.commit()

def load_metabolite_info():
    print("Loading metabolite information from MetaboLights")
    dataDir = 'test_data/'
    # start with one dataset at MetaboLights --> MTBLS2356 is Longnecker et al.
    study_id = 'MTBLS2356'
    try:
        ftp = FTP('ftp.ebi.ac.uk') #address from MetaboLights webpage
        ftp.login()
        ftpDataAddress = '/pub/databases/metabolights/studies/public/' + study_id
        ftp.cwd(ftpDataAddress)
        fileList = ftp.nlst() #can use this to make a list that will be searchable
        
        #start with the metadata about the samples 
        str = 's_' + study_id #this is the search string for the data files
        metadataFiles = [v for v in fileList if str in v] 
        metadataFiles = pd.DataFrame(metadataFiles,columns = ['files'])
        readFile = metadataFiles.loc[0,'files']

        # Is there a way to download an FTP file and not write it disk?
        writeFile = os.path.join(dataDir,'tempMetadata.txt')

        #MetaboLights will limit connections if I query too often
        with open(writeFile,'wb') as fp:
            try:
                retr_command = f"RETR {readFile}"
                ftp.retrbinary(retr_command, fp.write)
            except Exception as e: 
                print(f"Error during quit: {e}")
            except AttributeError as e: 
                print(f"AttributeError during quit: {e} - connection was likely already closed.")

        ftp.quit()
        
        # now read in the result (cannot remember why I did this in two steps)
        metadata_aboutSamples = pd.read_table(writeFile,delimiter = '\t')
        
        # pull what I can from the sample information at MetaboLights
        #for the database this is all need (is there a sample...)
        sampleNames  = metadata_aboutSamples['Source Name']

        #MetaboLights required samples to begin with a letter, I used 's' and need to strip that out 
        NewID_inMTBLS  = pd.to_numeric(sampleNames.str.strip('s')) 

        #convert the series into a dataframe:
        df = NewID_inMTBLS.reset_index() 
            
        #put the result into the database           
        session = Session()
        for index,row in tqdm(df.iterrows()):
            db = models.MetaboliteInfo()
            db.bottleID = f"{row['Source Name']}"
            db.dataSource = study_id 
            session.add(db)
        session.commit()
    except:
        print("MetaboLights did not allow connection, dummy data")
        session = Session()
        #pdb.set_trace()
        df = pd.DataFrame({'bottleID':['1033900707'],'dataSource':['MetaboLightsNotAvailable']})
        for index,row in tqdm(df.iterrows()):
            db = models.MetaboliteInfo()
            db.bottleID = row['bottleID']
            db.dataSource = row['dataSource']
            session.add(db)
        session.commit()       
        

def load_metaboliteUntargeted_info():
    print("Loading metabolite (untargeted) information from MetaboLights")
    dataDir = 'test_data/'
    # next dataset at MetaboLights --> MTBLS5228 is McParland et al.
    study_id = 'MTBLS5228'
    try:
        ftp = FTP('ftp.ebi.ac.uk') #address from MetaboLights webpage
        ftp.login()
        ftpDataAddress = '/pub/databases/metabolights/studies/public/' + study_id
        ftp.cwd(ftpDataAddress)
        fileList = ftp.nlst() #can use this to make a list that will be searchable
        
        #start with the metadata about the samples 
        str = 's_' + study_id #this is the search string for the data files
        metadataFiles = [v for v in fileList if str in v] 
        metadataFiles = pd.DataFrame(metadataFiles,columns = ['files'])
        readFile = metadataFiles.loc[0,'files']

        # Is there a way to download an FTP file and not write it disk?
        writeFile = os.path.join(dataDir,'tempMetadata.txt')

        with open(writeFile,'wb') as fp:
            try:
                retr_command = f"RETR {readFile}"
                ftp.retrbinary(retr_command, fp.write)
            except Exception as e: 
                print(f"Error during quit: {e}")
            except AttributeError as e: 
                print(f"AttributeError during quit: {e} - connection was likely already closed.")

        ftp.quit()
        
        # now read in the result (cannot remember why I did this in two steps)
        metadata_aboutSamples = pd.read_table(writeFile,delimiter = '\t')
        
        # pull what I can from the sample information at MetaboLights
        #for the database this is all need (is there a sample...)
        sampleNames  = metadata_aboutSamples['Source Name']

        #MetaboLights required samples to begin with a letter, I used 's' and need to strip that out 
        NewID_inMTBLS  = pd.to_numeric(sampleNames.str.strip('s')) 

        #convert the series into a dataframe:
        df = NewID_inMTBLS.reset_index() 
            
        #%run Kuj_MetabolightsData.py
        
        session = Session()
        for index,row in tqdm(df.iterrows()):
            db = models.MtabUntargeted()
            db.bottleID = f"{row['Source Name']}"
            db.dataSource = study_id 
            session.add(db)
        session.commit()
    except:
        print("MetaboLights did not allow connection, dummy data")
        session = Session()
        #pdb.set_trace()
        df = pd.DataFrame({'bottleID':['1033900707'],'dataSource':['MetaboLightsNotAvailable']})
        for index,row in tqdm(df.iterrows()):
            db = models.MetaboliteInfo()
            db.bottleID = row['bottleID']
            db.dataSource = row['dataSource']
            session.add(db)
        session.commit()       

if __name__ == "__main__":
    load_V4_sequencing_info()
    load_V1V2_sequencing_info()
    load_cyverse_info()
    load_discrete_info()
    load_metabolite_info()
    load_metaboliteUntargeted_info()
