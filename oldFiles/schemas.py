import datetime

from pydantic import BaseModel, Field


class AsvRelativeAbundanceBase(BaseModel):
    id: int
    asv_metadata_id: int
    asv_sample_id: int

    class Config:
        orm_mode = True


class AsvRelativeAbundanceCreate(AsvRelativeAbundanceBase):
    pass


class AsvRelativeAbundance(AsvRelativeAbundanceBase):
    abundance: float | None



class AsvMetadataBase(BaseModel):
    id: int

    class Config:
        orm_mode = True


class AsvMetadataCreate(AsvMetadataBase):
    pass


class AsvMetadata(AsvMetadataBase):
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


class AsvSampleBase(BaseModel):
    id: int
    niskin_id: int

    asv_rel_abundances: list[AsvRelativeAbundance] = []

    class Config:
        orm_mode = True


class AsvSampleCreate(AsvSampleBase):
    pass


class AsvSample(AsvSampleBase):
    data_type: str | None
    data_url: str | None
    sample_name: str | None
    fwd_primer: str | None
    rev_primer: str | None
    dada2name: str | None = Field(
        default=None, title="dada2name", max_length=500
    )


class NiskinBase(BaseModel):
    id: int
    cast_id: int

    asv_samples: list[AsvSample] = []

    class Config:
        orm_mode = True



class NiskinCreate(NiskinBase):
    pass


class Niskin(NiskinBase):
    old_bottle_id: str | None
    bottle_id: int | None
    location_gps_lat: float | None
    location_gps_long: float | None
    date_time_triggered: datetime.datetime | None
    depth_triggered: float | None
    nominal_depth: float | None
    temperature: float | None


class CastBase(BaseModel):
    cast_number: int | None
    cast_date: datetime.date | None
    mixed_layer_depth_value: float | None
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
    departure_date: datetime.date | None
    return_date: datetime.date | None
    target_lat: float | None
    target_long: float | None
    station: str | None
    cruise_id: str | None
    program: str | None



class CruiseCreate(CruiseBase):
    pass


class Cruise(CruiseBase):
    id: int
    casts: list[Cast] = []

    class Config:
        orm_mode = True


