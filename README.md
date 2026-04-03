# SargassoDB (branch movingAhead)

## 3 April 2026
Make a different branch to move ahead as kristaWorking is messing around with existing code to understand it.
## 2 April 2026
Have a basic query working. I think I am ready to start gathering up real BIOS-SCOPE data and setting up a database that can track what has been done over the years.

## updated 31 March 2026 (Krista)
While this is an older repository, it holds code that is able to generate a database (e.g., it works). Move forward with this. Work in a separate branch: KristaWorking
=======
## updated 30 March 2026 (Krista)
Actually this is useful as I can actually get this database to run which I could not do with the newer code.\
Keep this and move on from here.

Some basic steps:
```bash
venv\Scripts\activate
pip install -r requirements.txt (only once)
set SARGASSODB_CONFIG_FILE=%cd%\sargassodb\config.json (not sure if this is used here, but cannot hurt)
python populate_db.py (will take a while)

```

Will produce a database in sql_app.db

>>>>>>> d9e21dcf4c72af145b228863c0ab8d283daa76bf
## updated 13 March 2026 (Krista)
This is deprecated, use bioscope-portal instead.

--- 

This is the private data repository for the BIOS-SCOPE team.

It is built upon an SQLite database with the following entity relationships:

![Entity Relationship Diagram](images/ERD.png)

It also provides [FastAPI](https://fastapi.tiangolo.com/tutorial/) access to the database.
