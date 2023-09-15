import datetime

from pydantic import BaseModel, Field


class AsvMetadataBase(BaseModel):
    name: str
    sequence: str
    tax_kingdom: str | None = Field(
        default=None, title="tax_kingdom", max_length=300
    )
    tax_phylum: str | None = Field(
        default=None, title="tax_phylum", max_length=300
    )
    tax_class: str | None = Field(
        default=None, title="tax_class", max_length=300
    )
    tax_order: str | None = Field(
        default=None, title="tax_order", max_length=300
    )
    tax_family: str | None = Field(
        default=None, title="tax_family", max_length=300
    )
    tax_genus: str | None = Field(
        default=None, title="tax_genus", max_length=300
    )
    tax_comboname: str | None = Field(
        default=None, title="tax_comboname", max_length=1000
    )


class AsvMetadataCreate(AsvMetadataBase):
    pass


class AsvMetadata(AsvMetadataBase):
    id: int

    class Config:
        orm_mode = True


class AsvSampleBase(BaseModel):
    data_type: str
    data_url: str
    sample_name: str
    fwd_primer: str | None
    rev_primer: str | None
    dada2name: str | None = Field(
        default=None, title="dada2name", max_length=500
    )


class AsvSampleCreate(AsvSampleBase):
    pass


class AsvSample(AsvSampleBase):
    id: int
    niskin_id: int

    class Config:
        orm_mode = True


class NiskinBase(BaseModel):
    bottle_id: int
    old_bottle_id: str
    location_gps_lat: float
    location_gps_long: float
    date_time_triggered: datetime.datetime
    depth_triggered: float
    nominal_depth: float
    temperature: float

class NiskinCreate(NiskinBase):
    pass


class Niskin(NiskinBase):
    id: int
    cast_id: int

    asv_samples: list[AsvSample] = []

    class Config:
        orm_mode = True


class CastBase(BaseModel):
    cast_number: int
    cast_time: datetime.date
    mixed_layer_depth_value: float
    mixed_layer_depth_method: str | None = Field(default='dens_T2',
                                                 title="The method in which the mixed layer depth was measured",
                                                 max_length=300)


class CastCreate(CastBase):
    pass


class Cast(CastBase):
    id: int
    cruise_id: int
    niskins: list[Niskin] = []

    class Config:
        orm_mode = True


class CruiseBase(BaseModel):
    departure_date: datetime.date
    return_date: datetime.date
    target_lat: float
    target_long: float
    station: str
    cruise_id: str
    program: str



class CruiseCreate(CruiseBase):
    pass


class Cruise(CruiseBase):
    id: int
    casts: list[Cast] = []

    class Config:
        orm_mode = True


