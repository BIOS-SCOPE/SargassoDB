# SargassoDB
BIOS-SCOPE has been collecting data for ten years and needs a database to merge across datastreams. This code is designed to allow team members to look for a specific sample and see if data exist. For the moment, this only considers data collected from discrete samples. The output of the code includes the following:
1. Cruise
2. Date
3. bottleID (ten digit number: five digit cruise, three digit cast, two digit Niskin bottle)
4. V1V2 data: lane information
5. V4_16Sdata: lane information
6. V4_18Sdata: lane information
7. mtabData: repository number for targeted metabolites (known compounds, ~60 compoundd)
8. mtabDataUntargeted: repository number for untargeted metabolites (unknown features, 1000s of options)


## 8 April 2026
Opted to trim the sequencing files back to names without any suffixes as the use of suffixes varies.\
I have at least four options, so this function will remove them: ```one = one.removesuffix('.gz').removesuffix('.fastq').removesuffix('_fastqc.html').removesuffix('_fastqc.zip')```     

Basic steps in an Anaconda Prompt:
```bash
venv\Scripts\activate
python populate_db.py
python crud.py
python checkMatch.py
```

checkMatch.py will send out **BIOSSCOPE_checkMatch.csv** for easy browsing

To do list:
- [ ] How to force NewID to string in the database (and not when I read in the file)
- [ ] Add to checkMatch -> each sample should have R1 and R2 (forward and reverse primers)

## 7 April 2026
I can use ```checkMatch.ipynb``` to connect the sequence file list(s) from Luis with the database, and it becomes clear that I have relatively few matches so I need to look into this.
First though, pull this code into the main branch (but leave the other two branches: KristaWorking and movingAhead)

## 6 April 2026
Have this mostly ready as scripts only (so much faster than using Jupyter notebook). Basic steps in an Anaconda Prompt:

```bash
venv\Scripts\activate
pip install -r requirements.txt (just once)
python populate_db.py
python crud.py
```

## 5 April 2026
Can now pull in V1V2, V4, and metabolites data into the database and then export the results as a table. Ready to tidy this up into scripts that are not being run in Jupyter notebook

## 3 April 2026
Make a different branch to move ahead as KristaWorking is messing around with existing code to understand it.
So far, so good, I can merge two files (based on joining with fastq filename). Move on to searching in the discrete file for datatype.
Have a working prototype, now I need to figure out how to insert the filename information back into discrete (or a subset of discrete)

## 2 April 2026
Have a basic query working. I think I am ready to start gathering up real BIOS-SCOPE data and setting up a database that can track what has been done over the years.

## updated 31 March 2026 (Krista)

While this is an older repository, it holds code that is able to generate a database (e.g., it works). Move forward with this, though I will work in a separate branch: KristaWorking

## updated 30 March 2026 (Krista)
This is useful as I can get this database to run. Keep this and move on from here.

Some basic steps:
```bash
venv\Scripts\activate
pip install -r requirements.txt 
set SARGASSODB_CONFIG_FILE=%cd%\sargassodb\config.json (not sure if this is used here, but cannot hurt)
python populate_db.py (will take a while)

```

Will produce a database in sql_app.db

--- 
(original notes from Ben follow)
This is the private data repository for the BIOS-SCOPE team.

It is built upon an SQLite database with the following entity relationships:

![Entity Relationship Diagram](images/ERD.png)

It also provides [FastAPI](https://fastapi.tiangolo.com/tutorial/) access to the database.
