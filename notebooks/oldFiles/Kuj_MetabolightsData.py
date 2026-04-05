#!/usr/bin/env python
# coding: utf-8

# # MetaboLights (untargeted) to CMAP
# ## Krista Longnecker, 25 September 2025
# Modifying to get information I need for the SargassoDB 5 April 2026
# 

# Update to use with the BIOS-SCOPE data targeted metabolites data 
# MetaboLights has FTP access to their data files and that is easy enough to access, but there are some downstream steps needed to get all the station information.

#get_ipython().run_line_magic('reset', '-f')



import pandas as pd
import os
#import io
from ftplib import FTP
import re
from datetime import date, datetime, timedelta, timezone

# import pdb
#pdb.set_trace()

#make the data folder if it is not already there (make sure this is .gitignore, so it will not end up at GitHub)
folder = "..\\test_data"
os.chdir(".")

if os.path.isdir(folder):
    print("Data will go here (but should not be synced to GitHub): %s" % (os.getcwd()) + '\\' + folder)
else:
    os.mkdir(folder)


# ### Get MetaboLights files via FTP access

# start with one dataset at MetaboLights --> MTBLS2356 is Longnecker et al.
study_id = 'MTBLS2356'


#while testing, if the FTP command fails the connection is left open and the next command gives error
#error is: AttributeError: 'NoneType' object has no attribute 'sendall'
ftp = FTP('ftp.ebi.ac.uk') #address from MetaboLights webpage
ftp.login()
ftpDataAddress = '/pub/databases/metabolights/studies/public/' + study_id
ftp.cwd(ftpDataAddress)
#ftp.retrlines('LIST') #this will only print to console, not what I want
fileList = ftp.nlst() #can use this to make a list that will be searchable
#fileList

#start with the metadata about the samples so I can convert each sample to time/lat/lon/depth to match the CMAP requirements
str = 's_' + study_id #this is the search string for the data files
metadataFiles = [v for v in fileList if str in v] 
metadataFiles = pd.DataFrame(metadataFiles,columns = ['files'])
readFile = metadataFiles.loc[0,'files']

# metadataFiles: put them here 
# Is there a way to download an FTP file and not write it disk?
writeFile = 'data/' + 'tempMetadata.txt'

with open(writeFile,'wb') as fp:
    try:
        retr_command = f"RETR {readFile}"
        ftp.retrbinary(retr_command, fp.write)
    except Exception as e: 
        print(f"Error during quit: {e}")
    except AttributeError as e: 
        print(f"AttributeError during quit: {e} - connection was likely already closed.")

# now read in the result
metadata_aboutSamples = pd.read_table(writeFile,delimiter = '\t')


# # Now get the data files (more than one because things are split positive/negative ion mode...concatenate them later
# str = 'm_' + study_id #this is the search string for the data files
# dataFiles = [v for v in fileList if str in v] #Python syntax, will make a list
# dataFiles = pd.DataFrame(dataFiles,columns = ['files']) #I find the dataframe easier to manage than the list
# tsvFile = pd.DataFrame(); #this will be the data file

# #have to do some concatenating here bc positive and negative ion mode data
# for idx in range(len(dataFiles)):
    # readDataFile = dataFiles.loc[idx,'files']
    # writeDataFile = 'data/' + 'tempData.tsv'
          
    # with open(writeDataFile,'wb') as fp:
        # #try-except to make sure the FTP closes
        # try:
            # retr_command = f"RETR {readDataFile}"
            # #pdb.set_trace()
            # ftp.retrbinary(retr_command, fp.write)
        # except Exception as e: 
            # print(f"Error during quit: {e}")
    
    # #read in the temporary file and add to tsvFile file
    # tsvFile = pd.concat([tsvFile,pd.read_table(writeDataFile,delimiter = '\t')],ignore_index=True) #append is no longer valid



ftp.quit()  #close the FTP connection

#print("Have the data move on") 



# pull what I can from the sample information at MetaboLights
#for the database this is all need (is there a sample...)
sampleNames  = metadata_aboutSamples['Source Name']

#MetaboLights required samples to begin with a letter, I used 's' and need to strip that out 
NewID_inMTBLS  = pd.to_numeric(sampleNames.str.strip('s')) 

#convert the series into a dataframe:
forSargassoDB = NewID_inMTBLS.reset_index()
print("variable I want is forSargassoDB")




