import pandas as pd
import os
import re
import gc
import pdb #user with set_trace()
from datetime import datetime
from ftplib import FTP
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import contextlib
import xml.etree.ElementTree as ET #use this for the riNCBIonline function as their data are in XML file
#from sqlalchemy import MetaData

import models #if I use this, then syntax is models.SeqInfo
#from models import Base,SeqInfoV4 #here I can just use Base, SeqInfo
#import models as m #for this I would use m.Base, m.SeqInfo


'''
Populate the BIOS-SCOPE database with information, for now just where to 
find the files/databases where the information is located. Later will
probably be links to the actual data
Krista Longnecker 6 April 2026
Krista Longnecker 30 August 2026

'''

#start clean: delete existing file and make a new engine
print('Starting clean: delete database and create a new one') #: will fail if I have opened the data base with a Jupyter notebook'
data_dir = 'test_data'
dbName = 'sargasso.db'  

if os.path.exists(os.path.join(data_dir,dbName)):
    os.remove(os.path.join(data_dir,dbName)) 

# create a SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///test_data/sargasso.db"
#this will end up creating a new database everytime, but I need this for testing right now
#SQLALCHEMY_DATABASE_URL = f"sqlite:///test_data/new_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL) #, echo=True) #(turn off echo, gets annoying)

# create a session factory
SessionLocal = sessionmaker(bind=engine) #use this to differentiate from Session imported from sqlalchemy

#create the database
models.Base.metadata.create_all(engine)

 
# define the functions needed to run this script, start with the basics before going into the different tables

def trimSuffix(one):
    one = one.removesuffix('.gz').removesuffix('.fastq').removesuffix('_fastqc.html').removesuffix('_fastqc.zip')  
    return one
    
#parsing out the information in the filenames, use a function, this works with the NCBI filenames
def parseSampleNCBI(sample):
    #parsed = {} #use the next row and setup the dictionary first
    #even empty it is useful as I don't have to repeat all the NA options
    parsed = dict({'cruise5':'',
                   'cast':'',
                   'niskin':'',
                   'cruise':'',
                   'otherInfo':'',
                   'depth':'',
                   'sampleNumber':'',
                   'New_Bottle_ID':'',
                   'seqType':''})
    #start with 10 digits - cruise - cast - niskin and then underscores to note 18S_V4
    ru = [match.start() for match in re.finditer("_",sample)]
    #print(sample)
    if len(ru) ==2 & ru[0]==10:
        #pdb.set_trace()
        parsed['cruise5'] = sample[:5]
        parsed['cast'] = sample[5:8]
        parsed['niskin']= sample[8:10]        
        parsed['New_Bottle_ID'] = sample[:10]
        parsed['otherInfo'] = sample[ru[0]+1:]
        if '18S' in parsed['otherInfo']:
            parsed['seqType'] = 'V4_18s'
        elif '16S_V1V2' in parsed['otherInfo']:
            parsed['seqType'] = 'V1V2'
    elif (len(ru) ==2) & (ru[0] ==5):
        parsed['cruise5'] = sample[:5]
        parsed['depth'] = sample[ru[0]+1 : ru[1]]
        parsed['otherInfo'] = sample[ru[1] + 1:]
        parsed['New_Bottle_ID'] = None
            
    parsed = pd.DataFrame([parsed]) 
    return parsed

def changeToNone(val):
    if val is None: #already OK, return None again
        return None
    
    # Strip spaces and normalize to string
    clean = str(val).strip()
    
    # If you find known empty indicators, return than as None
    if clean in (['', 'nan', 'NaN', 'None', 'null', 'NULL', '<NA>']):
        return None
        
    return clean

def load_discrete_info(data_dir,fName):
    print('Loading discrete sample information')
    #data_dir = 'test_data/'
    #send fName into the function (see below...tired of updating for each function
    #fName = 'BATS_BS_COMBINED_MASTER_mini.xlsx' #use mini for testing
    #print('NOTE: using mini database for testing')
    #fName = 'BATS_BS_COMBINED_MASTER_latest.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),sheet_name='DATA'))

    session = SessionLocal()
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

    session = SessionLocal()
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
    session = SessionLocal()
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
            
    session = SessionLocal()
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
            
            
    session = SessionLocal()
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoV1V2()
        db.bottleID = f"{row['New_Bottle_ID']}" #f"{row['Source Name']}"
        db.cast = row['Cast']
        #pdb.set_trace()
        db.filename = row['V1V2_Sequencing_File']
        db.V1V2data = fName
        session.add(db)
    
    session.commit()

def riNCBIonline(data_dir,fName):
    # base_dir = 'd:/dropbox/github_niskin/SargassoDB/'
    # data_dir = 'test_data/'
    # fName = 'biosample_result.xml'
    tree = ET.parse(os.path.join(data_dir,fName))
    root = tree.getroot()

    parsed_records = []
    for biosample in root.findall(".//BioSample"):
        sample_id = biosample.attrib.get("id")

        # Initialize variables for this sample
        sample_name = None
        biosample_accession = None
        sra_id = None

        # Loop over the IDs section
        for id_tag in biosample.findall(".//Ids/Id"):
            db_type = id_tag.attrib.get("db")
            db_label = id_tag.attrib.get("db_label")
            is_primary = id_tag.attrib.get("is_primary")

            # pull what I need
            if db_label == "Sample name":
                sample_name = id_tag.text

            elif db_type == "BioSample" and is_primary == "1": #begins SAMN... this is the sample number
                biosample_accession = id_tag.text

            elif db_type == "SRA": #begins SRS...this is the sequence id
                sra = id_tag.text

        # Pull target keys out of the <Attributes> block
        for attr in biosample.findall(".//Attributes/Attribute"):
            attr_name = attr.attrib.get("attribute_name")
            if attr_name == "collection_date":
                collection_date = attr.text
            elif attr_name == "depth":
                depth = attr.text
            elif attr_name == "temperature":
                temp = attr.text
            elif attr_name == "salinity":
                sal = attr.text

        # Get submitter information (will be useful in house)
        contact_node = biosample.find(".//Owner/Contacts/Contact/Name")
        if contact_node is not None:
            first_node = contact_node.find("First")
            last_node = contact_node.find("Last")

            first_name = first_node.text if first_node is not None else ""
            last_name = last_node.text if last_node is not None else ""
            contact_name = f"{first_name} {last_name}".strip()

        # Append collected data to our list
        parsed_records.append({
            "id": sample_id,
            "biosample": biosample_accession,
            "sample": sample_name,
            "dateCollected":collection_date,
            "depth": depth,
            "temp":temp,
            "sal":sal,
            "sra": sra,
            "submitter":contact_name
        })

    dfNCBI = pd.DataFrame(parsed_records)
    
    #now ready to put this into the database
    session = SessionLocal()
    for index,row in tqdm(dfNCBI.iterrows()):
        db = models.SeqInfoNCBIonline()
        db.biosample = row['biosample'] 
        db.sample = row['sample']
        session.add(db)
    
    session.commit()
    
    
def riNCBIinhouse(data_dir,fName):
    print('Loading NCBI from in-house information')
    #This is the BIOS-SCOPE list (from Google) one what is at NCBI
    #fNameLOGncbi = 'BIOS-SCOPE-NCBI_Log_Nov2024.xlsx'
    df = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName)))
    #tidy up - make sure New_Bottle_ID is an integer
    df['New_Bottle_ID'] = df['New_Bottle_ID'].astype('Int64')
           
    #now ready to put this into the database (use iterrows bc the bulk insert will do some overwriting that I don't like)
    session = SessionLocal()
    #for index, row in tqdm(dfLOGncbi.iterrows(), total=len(dfLOGncbi)): #use this for progress bar
    for index, row in tqdm(df.iterrows()):
        db = models.SeqInfoNCBIinhouse()

        db.biosample = changeToNone(row['Biosample'])
        db.cruise5 = row['Cruise '] #note the trailing space
        db.sampleV1V2 = row['Sample name V1V2']
        db.sraV1V2 = row['SRA_16S_V1V2']
        db.seqV1V2 = row['V1V2_Sequencing_File']
        db.sampleV416s = row['Sample name V4']
        db.sraV416s = row['SRA_16S_V4']
        db.seqV416s = row['V4_Sequencing_File']
        db.firstReference = row['Reference (1st used in)']
        db.bottleID = changeToNone(row['New_Bottle_ID'])
        session.add(db)
        # except:
        #     pdb.set_trace()
    
    session.commit()
    
def riLTTtableS1(data_dir,fName):
    print('Loading Table S1 from LTT paper')
    #Table S1 in the LTT paper has still more information about sequences
    #fNameTableS1LTT = 'LTTpaper/Table_S1_Accession_SampleID_numbers.xlsx'
    dfLTTs1 = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName),skiprows=1))
    #pdb.set_trace()
    #tidy up - make sure some of these are integers (should I just do that when I map them using class? 
    dfLTTs1['Sample.ID'] = dfLTTs1['Sample.ID'].astype('Int64')
    dfLTTs1[['Year','Month','Depth']] = dfLTTs1[['Year','Month','Depth']].astype('Int64')
    
    #now ready to put this into the database
    session = SessionLocal()
    for index, row in tqdm(dfLTTs1.iterrows()):
        db = models.SeqInfoLTTs1()

        db.biosample = row['BioSample']
        db.sraV1V2 = row['SRA_16S_V1V2']
        db.bottleID = row['Sample.ID']
        db.year = row['Year']
        db.month = row['Month']
        db.depth = row['Depth']
        session.add(db)
    
    session.commit()
    
def riLTTdeepSeq(data_dir,fName):
    print('Loading Table S11 on deep sequencing in LTT paper')
    #Table S11 in the LTT paper has information about the deep sequencing
    #fNameTableDeep = 'LTTpaper/Table_S1_Accession_SampleID_numbers.xlsx'
    dfLTTdeep = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName)))
    #tidy up - make sure some of these are integers (should I just do that when I map them using class? 
    # pdb.set_trace()
    dfLTTdeep['Sample.ID'] = dfLTTdeep['Sample.ID'].astype('Int64')
    dfLTTdeep[['Year','Month','Depth']] = dfLTTdeep[['Year','Month','Depth']].astype('Int64')
    
    #now ready to put this into the database
    session = SessionLocal()
    for index, row in tqdm(dfLTTdeep.iterrows()):
        db = models.SeqInfoNCBIinhouse()
        db.sample = row['title']
        db.bottleID = row['Sample.ID']
        db.biosample = row['BioSample']
        db.sraV1V2 = row['SRA_16S_V1V2']
        db.year = row['Year']
        db.month = row['Month']
        db.depth = row['Depth']
        session.add(db)
    
    session.commit()


def riUnreleased(data_dir,fName):
    print('Loading unreleased data from NCBI')
    dfUnreleased = pd.DataFrame(pd.read_excel(os.path.join(data_dir,fName)))
    #tidy up - make sure some of these are integers (should I just do that when I map them using class? 
    #dfUnreleased['BioSample.name'] = dfUnreleased['BioSample.name'].astype('Int64')
    
    #now ready to put this into the database
    session = SessionLocal()
    for index, row in tqdm(dfUnreleased.iterrows()):
        db = models.NCBIunreleased()
        db.title = row['Title']
        db.bottleID = row['BioSample.name']
        db.biosample = row['Accession']
        db.sraV1V2 = row['SRA']
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
    #startClean() #delete existing db file and make a new one (with engine/session steps)

    #setup the file names ahead of time and then send that into each function
    data_dir = 'test_data/'
    fNameSeqLog = 'BIOS-SCOPE DNA Master 2026.07.20.xlsx' 
    fNameCyverse = 'filelist_concatenated.csv'
    fNameNCBIonline = 'biosample_result.xml'
    fNameNCBIinhouse = 'BIOS-SCOPE-NCBI_Log_Nov2024.xlsx'
    fNameTableS1LTT = 'LTTpaper/Table_S1_Accession_SampleID_numbers.xlsx'
    fNameLTTdeep = 'LTTpaper/Table_S11_Accession_Deep_Seq.xlsm'
    fNameUnreleased = 'NCBIunreleased.xlsx'
    
    fNameDiscrete = 'BATS_BS_COMBINED_MASTER_mini.xlsx' #use mini for testing
    #fNameDiscrete = 'BATS_BS_COMBINED_MASTER_latest.xlsx'
    
    #load_discrete_info(data_dir,fNameDiscrete)
    
    #load_V4_16S_sequencing_info(data_dir,fNameSeqLog)
    #load_V4_18S_sequencing_info(data_dir,fNameSeqLog)
    #load_V1V2_sequencing_info(data_dir,fNameSeqLog)
    #load_cyverse_info(data_dir,fNameCyverse)
    #load_metabolite_info(data_dir)
    #load_metaboliteUntargeted_info(data_dir)
    #load_sequencing_info(data_dir,fNameSeqLog)
    
    riNCBIonline(data_dir,fNameNCBIonline)
    riNCBIinhouse(data_dir,fNameNCBIinhouse)
    #riLTTtableS1(data_dir,fNameTableS1LTT)
    #riLTTdeepSeq(data_dir,fNameLTTdeep)
    #riUnreleased(data_dir,fNameUnreleased)