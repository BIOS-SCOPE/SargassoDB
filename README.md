# SargassoDB (branch KristaWorking)

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

## updated 13 March 2026 (Krista)
This is deprecated, use bioscope-portal instead.

--- 

This is the private data repository for the BIOS-SCOPE team.

It is built upon an SQLite database with the following entity relationships:

![Entity Relationship Diagram](images/ERD.png)

It also provides [FastAPI](https://fastapi.tiangolo.com/tutorial/) access to the database.
