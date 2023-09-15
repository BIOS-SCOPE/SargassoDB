from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Cruise(Base):
    __tablename__ = 'cruises'
    id = Column(Integer, primary_key=True, index=True)
    program = Column(String)
    cruise_id = Column(String)
    station = Column(String)
    target_lat = Column(String)
    target_long = Column(String)
    departure_date = Column(Date)
    return_date = Column(Date)
    casts = relationship('Cast', back_populates='cruise')


class Cast(Base):
    __tablename__ = 'casts'
    id = Column(Integer, primary_key=True, index=True)
    cast_number = Column(Integer)
    cast_date = Column(Date)
    mixed_layer_depth_value = Column(Float)
    mixed_layer_depth_method = Column(String, server_default='dens_T2')

    niskins = relationship('Niskin', back_populates='cast')
    cruise_id = Column(Integer, ForeignKey('cruises.id'))
    cruise = relationship('Cruise', back_populates='casts')


class Niskin(Base):
    __tablename__ = 'niskins'
    id = Column(Integer, primary_key=True, index=True)
    bottle_id = Column(Integer, nullable=False)
    old_bottle_id = Column(String)
    niskin_number = Column(Integer)
    location_gps_lat = Column(Float)
    location_gps_long = Column(Float)
    date_time_closed = Column(DateTime)
    depth_triggered = Column(Float)
    nominal_depth = Column(Integer)
    temperature = Column(Float)

    cast_id = Column(Integer, ForeignKey('casts.id'))
    cast = relationship('Cast', back_populates='niskins')

    asv_samples = relationship('AsvSample', back_populates='niskin')


class AsvSample(Base):
    __tablename__ = 'asv_samples'
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(10))  # 16S or 18S
    sample_name = Column(String)
    fwd_primer = Column(String)
    rev_primer = Column(String)
    data_url = Column(String)
    dada2name = Column(String, index=True)


    niskin_id = Column(Integer, ForeignKey('niskins.id'))
    niskin = relationship('Niskin', back_populates='asv_samples')

    asv_rel_abundances = relationship("AsvRelativeAbundance", back_populates="asv_sample")

    # sequencing_run_id = Column(Integer, ForeignKey('sequencing_runs.id'))
    # sequencing_run = relationship('SequencingRun', back_populates='samples')


class AsvMetadata(Base):
    __tablename__ = 'asv_metadatas'
    id = Column(Integer, primary_key=True, index=True)
    sequence = Column(String, nullable=False)
    tax_kingdom = Column(String(length=300))
    tax_phylum = Column(String(length=300))
    tax_class = Column(String(length=300))
    tax_order = Column(String(length=300))
    tax_family = Column(String(length=300))
    tax_genus = Column(String(length=300))
    tax_comboname = Column(String(length=1000))


class AsvRelativeAbundance(Base):
    __tablename__ = 'asv_rel_abundances'
    id = Column(Integer, primary_key=True, index=True)
    abundance = Column(Float, nullable=False)

    asv_metadata_id = Column(Integer, ForeignKey('asv_metadatas.id'))
    asv_metadata = relationship('AsvMetadata')

    asv_sample_id = Column(Integer, ForeignKey('asv_samples.id'))
    asv_sample = relationship('AsvSample', back_populates='asv_rel_abundances')
