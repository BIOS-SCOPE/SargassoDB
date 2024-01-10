import sqlalchemy
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import models
import schemas
import crud
from io import StringIO

from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

templates = Jinja2Templates(directory="templates")
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# @app.get("/")
# async def root():
 #    return {"message": "Hello World"}

@app.get("/",response_class=HTMLResponse)




async def home(request: Request):
    message = "Welcome to the BIOS-SCOPE data website"

    # get and format current local date and time
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    testin = read_niskin(niskin_id= 1, db= SessionLocal())
    testin2 = read_niskin(niskin_id=1, db=SessionLocal())
    #testin2 = sample_depths()
    #testin = Niskin.__table__.columns
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "message": message,
            "current_time": current_time,
            "testin": testin,
            "testin2":testin2


        }
)



@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/cruises/", response_model=schemas.Cruise)
def create_cruise(cruise: schemas.CruiseCreate, db: Session = Depends(get_db)):
    return crud.create_cruise(db=db, cruise=cruise)


@app.get("/cruises/", response_model=list[schemas.Cruise])
def read_cruises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cruises = crud.get_cruises(db, skip=skip, limit=limit)
    return cruises


@app.get("/cruises/{cruise_id}", response_model=schemas.Cruise)
def read_cruise(cruise_id: int, db: Session = Depends(get_db)):
    db_cruise = crud.get_cruise(db, cruise_id=cruise_id)
    if db_cruise is None:
        raise HTTPException(status_code=404, detail="Cruise not found")
    return db_cruise


@app.post("/cruises/{cruise_id}/casts/", response_model=schemas.Cast)
def create_cast_for_cruise(
    cruise_id: int, cast: schemas.CastCreate, db: Session = Depends(get_db)
):
    return crud.create_cast(db=db, cast=cast, cruise_id=cruise_id)


@app.get("/casts/", response_model=list[schemas.Cast])
def read_casts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    casts = crud.get_casts(db, skip=skip, limit=limit)
    return casts


@app.get("/casts/{cast_id}", response_model=schemas.Cast)
def read_cast(cast_id: int, db: Session = Depends(get_db)):
    db_cast = crud.get_cast(db, cast_id=cast_id)
    if db_cast is None:
        raise HTTPException(status_code=404, detail="Cast not found")
    return db_cast



@app.post("/casts/{cast_id}/niskins/", response_model=schemas.Niskin)
def create_niskin_for_cast(
    cast_id: int, niskin: schemas.NiskinCreate, db: Session = Depends(get_db)
):
    return crud.create_niskin(db=db, niskin=niskin, cast_id=cast_id)


@app.get("/niskins/", response_model=list[schemas.Niskin])
def read_niskins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    niskins = crud.get_niskins(db, skip=skip, limit=limit)
    return niskins


@app.get("/niskins/{niskin_id}", response_model=schemas.Niskin)
def read_niskin(niskin_id: int, db: Session = Depends(get_db)):
    db_niskin = crud.get_niskin(db, niskin_id=niskin_id)
    if db_niskin is None:
        raise HTTPException(status_code=404, detail="Niskin not found")
    #query = print([db_niskin.bottle_id])
    #return db_niskin
    return db_niskin.__table__.c.keys() #works
    #return db_niskin.__table__.indexes #works
    #return query

@app.get("/niskins/{master_bottle_file_id}", response_model=schemas.Niskin)
def read_niskin_by_master_bottle_id(master_bottle_file_id: int, db: Session = Depends(get_db)):
    db_niskin = crud.get_niskin_by_master_bottle_file_id(db, master_bottle_file_id=master_bottle_file_id)
    if db_niskin is None:
        raise HTTPException(status_code=404, detail="Niskin not found")
    return db_niskin

@app.get('/niskins/{depth_1}/{depth_2}', response_model=list[schemas.Niskin])
def read_niskins_by_depth_range(depth_1: int, depth_2: int, db: Session = Depends(get_db)):
    db_niskins = crud.get_niskin_by_depth_range(db, depth_1=depth_1, depth_2=depth_2)
    if not db_niskins:
        raise HTTPException(status_code=404, detail=f"Niskins not found between depths {depth_1} and {depth_2}")
    return db_niskins


@app.post("/niskins/{niskin_id}/asv_samples/", response_model=schemas.AsvSample)
def create_asv_sample_for_niskin(
    niskin_id: int, asv_sample: schemas.AsvSampleCreate, db: Session = Depends(get_db)
):
    return crud.create_asv_sample(db=db, asv_sample=asv_sample, niskin_id=niskin_id)

@app.get("/asv_samples/", response_model=list[schemas.AsvSample])
def read_asv_samples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    asv_samples = crud.get_asv_samples(db, skip=skip, limit=limit)
    return asv_samples

@app.get("/asv_samples/{asv_sample_id}", response_model=schemas.AsvSample)
def read_asv_sample(asv_sample_id: int, db: Session = Depends(get_db)):
    db_asv_sample = crud.get_asv_sample(db, asv_sample_id=asv_sample_id)
    if db_asv_sample is None:
        raise HTTPException(status_code=404, detail="ASV sample not found")
    return db_asv_sample





@app.get("/asv_metadatas/", response_model=list[schemas.AsvMetadata])
def read_asv_metadatas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    asv_metadatas = crud.get_asv_metadatas(db, skip=skip, limit=limit)
    return asv_metadatas


def sample_depths():
    dfdepth = pd.read_csv('test_data/niskin_data_2023-09-13.csv',usecols=[9])
    dfdepthu = dfdepth.drop_duplicates()
    return dfdepthu[0:11]