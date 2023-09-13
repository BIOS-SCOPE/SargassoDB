from sqlalchemy.orm import Session
import models
import schemas



def get_cruise(db: Session, cruise_id: int):
    return db.query(models.Cruise).filter(models.Cruise.id == cruise_id).first()


def get_cruises(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cruise).offset(skip).limit(limit).all()


def create_cruise(db: Session, cruise: schemas.CruiseCreate):
    db_cruise = models.Cruise(**cruise.dict())
    db.add(db_cruise)
    db.commit()
    db.refresh(db_cruise)
    return db_cruise


def get_cast(db: Session, cast_id: int):
    return db.query(models.Cast).filter(models.Cast.id == cast_id).first()


def get_casts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cast).offset(skip).limit(limit).all()


def create_cast(db: Session, cast: schemas.CastCreate, cruise_id: int):
    db_cast = models.Cast(**cast.dict(), cruise_id=cruise_id)
    db.add(db_cast)
    db.commit()
    db.refresh(db_cast)
    return db_cast


def get_niskin(db: Session, niskin_id: int):
    return db.query(models.Niskin).filter(models.Niskin.id == niskin_id).first()


def get_niskin_by_master_bottle_file_id(db: Session, master_bottle_file_id: int):
    return db.query(models.Niskin).filter(models.Niskin.master_bottle_file_id == master_bottle_file_id).first()


def get_niskins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Niskin).offset(skip).limit(limit).all()


def create_niskin(db: Session, niskin: schemas.NiskinCreate, cast_id: int):
    db_niskin = models.Niskin(**niskin.dict(), cast_id=cast_id)
    db.add(db_niskin)
    db.commit()
    db.refresh(db_niskin)
    return db_niskin


def get_asv_sample(db: Session, asv_sample_id: int):
    return db.query(models.AsvSample).filter(models.AsvSample.id == asv_sample_id).first()


def get_asv_samples(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AsvSample).offset(skip).limit(limit).all()


def create_asv_sample(db: Session, asv_sample: schemas.AsvSampleCreate, niskin_id: int):
    db_asv_sample = models.AsvSample(**asv_sample.dict(), niskin_id=niskin_id)
    db.add(db_asv_sample)
    db.commit()
    db.refresh(db_asv_sample)
    return db_asv_sample


def get_asv_metadata(db: Session, asv_metadata_id: int):
    return db.query(models.AsvMetadata).filter(models.AsvMetadata.id == asv_metadata_id).first()


def get_asv_metadatas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AsvMetadata).offset(skip).limit(limit).all()


def create_asv_metadata(db: Session, asv_metadata: schemas.AsvMetadataCreate):
    db_asv_metadata = models.AsvMetadata(**asv_metadata.dict())
    db.add(db_asv_metadata)
    db.commit()
    db.refresh(db_asv_metadata)
    return db_asv_metadata



