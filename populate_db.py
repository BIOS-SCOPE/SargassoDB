import pandas as pd
import os
import pdb #user with set_trace()
from datetime import datetime
from ftplib import FTP
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import contextlib
#from sqlalchemy import MetaData

import models #if I use this, then syntax is models.SeqInfo
#from models import Base,SeqInfoV4 #here I can just use SeqInfo

'''
Populate the BIOS-SCOPE database with information, for now just where to 
find the files/databases where the information is located. Later will
probably be links to the actual data
Krista Longnecker 6 April 2026
Krista Longnecker 30 August 2026

'''

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL) #, echo=True) #(turn off echo, gets annoying)

# create a session factory
Session = sessionmaker(bind=engine)

#create the database
models.Base.metadata.create_all(engine)
    
##I think (from Stack Overflow) this will empty the database before I start
# meta = MetaData()

# with contextlib.closing(engine.connect()) as con:
#     trans = con.begin()
#     for table in reversed(meta.sorted_tables):
#         con.execute(table.delete())
#     trans.commit()

   
# # define the functions needed to run this script
   
def delete_db():
    print('Deleting database: does not work nicely with Jupyter notebook script open')
    db_path = 'test_data/sargssso.db'
    if os.path.exists(db_path):
        os.unlink(db_path)
        
def trimSuffix(one):
    one = one.removesuffix('.gz').removesuffix('.fastq').removesuffix('_fastqc.html').removesuffix('_fastqc.zip')  
    return one
    
def load_discrete_info(data_dir,fName):
    print('Loading discrete sample information')
    #data_dir = 'test_data/'
    #send fName into the function
    #fName = 'BATS_BS_COMBINED_MASTER_mini.xlsx' #use mini for testing
    #print('NOTE: using mini database for testing')
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

def load_sequencing_info(data_dir,fName):
    print('Getting general sequencing information')
    #data_dir = 'test_data/'
    #fName = 'V4_dada2_read_info_03052026.xlsx'
    #fName = 'BIOS-SCOPE DNA Master 2026.03.10.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),header=0,
                                   sheet_name = 'BIOS-SCOPE Samples 2014-2023',
                                   dtype={'New_Bottle_ID':str,'Type':str,'Location':str,'Status':str,'Extracted':str,'Analyst1':str}))
           
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !

    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoBasics()
        db.bottleID = row['New_Bottle_ID'] 
        db.sType = row['Type']
        db.location = row['Location']
        db.status = row['Status']
        db.extracted = row['Extracted']
        db.analyst1 = row['Analyst1']
        session.add(db)
    
    session.commit()
    
def load_V4_18S_sequencing_info(data_dir,fName):
    print('Loading V4_18S sequencing information')
    #data_dir = 'test_data/'
    #fName = 'V4_dada2_read_info_03052026.xlsx'
    #fName = 'BIOS-SCOPE DNA Master 2026.07.20.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),header=0,
                                   sheet_name = 'BIOS-SCOPE Samples 2014-2023',
                                   dtype={'New_Bottle_ID':str,'Cruise':str,'Cast':str,'Depths':str}))                                   
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !
       
    #have multiple possible endings to each filename nothing, fastaq, fastaq.gz...change that
    for index,row in df.iterrows():
        one = row['V4_18s_Sequencing_File']
        if not pd.isna(one):
            df.loc[index,'V4_18s_Sequencing_File'] = trimSuffix(one)      

    #pdb.set_trace()
    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV4_18S()
        db.bottleID = row['New_Bottle_ID'] 
        db.cast = row['Cast']
        db.filename = row['V4_18s_Sequencing_File']           
        db.V4_18Sdata = fName
        session.add(db)
    
    session.commit()
        
def load_V4_16S_sequencing_info(data_dir,fName):
    print('Loading V4_16S sequencing information')
    #data_dir = 'test_data/'
    #fName = 'V4_dada2_read_info_03052026.xlsx'
    #fName = 'BIOS-SCOPE DNA Master 2026.07.20.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),header=0,
                                   sheet_name = 'BIOS-SCOPE Samples 2014-2023',
                                   dtype={'New_Bottle_ID':str,'Cruise':str,'Cast':str,'Depths':str}))                                   
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !

    #have multiple possible endings to each filename nothing, fastaq, fastaq.gz...change that
    for index,row in df.iterrows():
        one = row['V4_16s_Sequencing_File']
        if not pd.isna(one):
            df.loc[index,'V4_16s_Sequencing_File'] = trimSuffix(one)
            
    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV4_16S()
        db.bottleID = row['New_Bottle_ID'] 
        db.cast = row['Cast']
        db.filename = row['V4_16s_Sequencing_File']
        db.V4_16Sdata = fName
        session.add(db)
    
    session.commit()
    
def load_V1V2_sequencing_info(data_dir,fName):
    print('Loading V1V2 sequencing information')
    #data_dir = 'test_data/'
    #fName = 'BIOS-SCOPE DNA Master 2026.07.20.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),header=0,
                                   sheet_name = 'BIOS-SCOPE Samples 2014-2023',
                                   dtype={'New_Bottle_ID':str,'Cruise':str,'Cast':str,'Depths':str}))  
    #strip the @#%@#^$ spaces in headers
    df.columns = df.columns.str.replace(' ','') ## actual file has a space AFTER Bottle ID !
        
    #have multiple possible endings to each filename nothing, fastaq, fastaq.gz...change that
    for index,row in df.iterrows():
        one = row['V1V2_Sequencing_File']
        if not pd.isna(one):
            df.loc[index,'V1V2_Sequencing_File'] = trimSuffix(one)  
            
            
    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV1V2()
        db.bottleID = f"{row['New_Bottle_ID']}" #f"{row['Source Name']}"
        db.cast = row['Cast']
        #pdb.set_trace()
        db.filename = row['V1V2_Sequencing_File']
        db.V1V2data = fName
        session.add(db)
    
    session.commit()

def load_cyverse_info(data_dir,fName):
    #use this to check that I found all I expected
    print('Loading sequencing information')
    #dataDir = 'test_data/'
    #fName = 'filelist_concatenated.csv'
    df = pd.read_csv(os.path.join(data_dir,fName))
    
    #have multiple possible endings to each filename nothing, fastaq, fastaq.gz...change that
    for index,row in df.iterrows():
        one = row['filename']
        if not pd.isna(one):
            df.loc[index,'filename'] = trimSuffix(one)
            
    session = Session()
    for index, row in tqdm(df.iterrows()):
        db = models.CyverseInfo()
        db.filename = row['filename'] 
        db.source = row['source']
        db.V1V2_found = row['source'] #actually need blank, but this will work for now
        db.V4_16S_found = row['source']
        db.V4_18S_found = row['source']
        session.add(db)
    
    session.commit()

def load_metabolite_info(data_dir):
    print("Loading metabolite information from MetaboLights")
    #dataDir = 'test_data/'
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
        

def load_metaboliteUntargeted_info(data_dir):
    print("Loading metabolite (untargeted) information from MetaboLights")
    #dataDir = 'test_data/'
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
        
        #Erin also had blanks and boooled samples, remove those and make a list (added 4/6/2026)
        #Don't really want the extra steps, but that is how I can understand this
        sampleList = [x for x in sampleNames if not x.startswith(('spool','sblank','smqblank'))]
        sampleNames = pd.Series(sampleList)
        
        #MetaboLights required samples to begin with a letter, I used 's' and need to strip that out 
        NewID_inMTBLS  = pd.to_numeric(sampleNames.str.strip('s')) 

        #convert the series into a dataframe:
        df = NewID_inMTBLS.reset_index() 
        df.columns = ['index','bottleID'] #somehow lost column labels
         
        session = Session()
        for index,row in tqdm(df.iterrows()):
            db = models.MtabUntargetedInfo()
            db.bottleID = f"{row['bottleID']}" #seems like there should be a btter way to do this
            db.dataSource = study_id 
            session.add(db)
        session.commit()
    except:
        print("MetaboLights did not allow connection OR some other error")
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
    delete_db() #will not work in jupyter notebook

    #setup the file names ahead of time and then send that into each function
    data_dir = 'test_data/'
    fNameSeqLog = 'BIOS-SCOPE DNA Master 2026.07.20.xlsx' 
    fNameCyverse = 'filelist_concatenated.csv'
    
    fNameDiscrete = 'BATS_BS_COMBINED_MASTER_mini.xlsx' #use mini for testing
    #fNameDiscrete = 'BATS_BS_COMBINED_MASTER_latest.xlsx'
    
    load_V4_16S_sequencing_info(data_dir,fNameSeqLog)
    load_V4_18S_sequencing_info(data_dir,fNameSeqLog)
    load_V1V2_sequencing_info(data_dir,fNameSeqLog)
    load_cyverse_info(data_dir,fNameCyverse)
    load_discrete_info(data_dir,fNameDiscrete)
    #load_metabolite_info(data_dir)
    #load_metaboliteUntargeted_info(data_dir)
    load_sequencing_info(data_dir,fNameSeqLog)