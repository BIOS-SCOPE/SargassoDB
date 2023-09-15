import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, time
import models


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Session = sessionmaker()

Session.configure(bind=engine)


def load_cruise_data():
    print('Loading cruise data')
    df = pd.read_csv('test_data/cruise_data.csv')
    session = Session()
    for index, row in df.iterrows():
        db_cruise = models.Cruise()
        db_cruise.program = row['program']
        db_cruise.cruise_id = row['cruise_id']
        session.add(db_cruise)
    session.commit()


def load_cast_data():
    print('Loading cast data')
    df = pd.read_csv('test_data/casts.csv')
    session = Session()
    for index, row in df.iterrows():
        db_cruise = session.query(models.Cruise).filter(models.Cruise.cruise_id == row['cruise_id']).first()
        db_cast = models.Cast()
        if not pd.isna(row['date']):
            db_cast.cast_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
        db_cast.cast_number = row['cast_number']
        db_cruise.casts.append(db_cast)
    session.commit()


def load_niskin_data():
    print('Loading niskin data')
    df = pd.read_csv('test_data/niskin_data_2023-09-13.csv', low_memory=False)
    session = Session()
    for index, row in df.iterrows():
        db_cruise = session.query(models.Cruise).filter(models.Cruise.cruise_id == row['cruise_id']).first()
        db_cast = session.query(models.Cast).filter(models.Cast.cruise_id == db_cruise.id,
                                                    models.Cast.cast_number==row['cast_number']).first()
        db_niskin = models.Niskin()
        db_niskin.old_bottle_id = row['old_bottle_id']
        db_niskin.bottle_id = row['bottle_id']
        db_niskin.niskin_number = row['niskin_number']
        if not pd.isna(row['time(UTC)']):
            date_of_cast = db_cast.cast_date
            time_str = f"{int(row['time(UTC)']):04d}"
            hours = int(time_str[:2])
            minutes = int(time_str[2:])
            db_niskin.date_time_closed = datetime.combine(date_of_cast, time(hours, minutes, 0))

        db_niskin.location_gps_lat = row['latN']
        db_niskin.location_gps_long = row['lonW']
        db_niskin.depth_triggered = row['Depth']
        db_niskin.nominal_depth = row['Nominal_Depth']
        db_niskin.temperature = row['Temp']
        db_cast.niskins.append(db_niskin)
    session.commit()

def load_asv_metadata():
    print('Loading ASV metadata')
    df = pd.read_csv('test_data/bats49month_taxonomy_combonames_May_28_2021.csv')
    session = Session()
    for index, row in df.iterrows():

        db_asv_metadata = models.AsvMetadata()
        db_asv_metadata.name = row['name']
        db_asv_metadata.sequence = row['sequence']
        db_asv_metadata.tax_kingdom = row['tax_kingdom']
        db_asv_metadata.tax_phylum = row['tax_phylum']
        db_asv_metadata.tax_class = row['tax_class']
        db_asv_metadata.tax_order = row['tax_order']
        db_asv_metadata.tax_family = row['tax_family']
        db_asv_metadata.tax_genus = row['tax_genus']
        db_asv_metadata.tax_comboname = row['tax_comboname']
        session.add(db_asv_metadata)
    session.commit()


def load_asv_samples():
    print('Loading ASV sample names')
    df = pd.read_csv('test_data/asv_samples.csv')
    session = Session()
    for index, row in df.iterrows():
        #find the niskin by master bottle file
        db_niskin = session.query(models.Niskin).filter(models.Niskin.bottle_id == row['MasterBottlefileID']).first()
        #find the cast by the niskin id
        db_cast = db_niskin.cast.mixed_layer_depth_value = row['MLD_densT2']

        db_asv_sample = models.AsvSample()
        db_asv_sample.dada2name = row['dada2name']
        db_asv_sample.sample_name = row['sample_name']
        db_asv_sample.niskin = db_niskin
        session.add(db_asv_sample)
    session.commit()


def load_rel_abundances():
    print('Loading ASV relative abundances')
    df = pd.read_csv('test_data/mini_test_asv_rel_abundances.csv')
    long_format = pd.melt(df, id_vars=['short_name', 'seqs'], var_name= 'sample_name', value_vars=df.columns[2:])
    session = Session()
    counter = 0
    for index, row in long_format.iterrows():
        db_asv_sample = session.query(models.AsvSample).filter(models.AsvSample.sample_name == row['sample_name']).first()
        #TODO this is going to be a horror show for speed, so need a better way to find the sequences
        db_asv_metadata = session.query(models.AsvMetadata).filter(models.AsvMetadata.sequence == row['seqs']).first()

        db_rel_abundance = models.AsvRelativeAbundance()
        db_rel_abundance.abundance = row['value']
        db_rel_abundance.asv_sample = db_asv_sample
        db_rel_abundance.asv_metadata = db_asv_metadata
        session.add(db_rel_abundance)
        counter += 1

        if counter % 10000 ==0:
            session.commit()
            print(f'Committed {counter} records')
    session.commit()
    print(f'Committed {counter} records')





if __name__ == "__main__":
    load_asv_metadata()
    load_cruise_data()
    load_cast_data()
    load_niskin_data()
    load_asv_samples()
    load_rel_abundances()