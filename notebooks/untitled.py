#working.py

with Session(engine) as session:
    # Get one NewID from the master table
    bottle = session.get(DiscreteInfo, 1) 
    
    print(f"Bottle ID: {bottle.bottleID}")
    print(f"Depth: {bottle.nominalDepth}")
    
    # 2. Instantly loop through all sequencing runs linked to this bottle!
    # (SQLAlchemy automatically handles the database join behind the scenes)
    for run in bottle.v4_16s_runs:
        print(f" -> Found Sequence File: {run.filename}")
        print(f" -> V4 16S Data: {run.V4_16Sdata}")
