import datetime

from pydantic import BaseModel, Field

#KL 3/30/2026 added and changed from name: int | None and so on to this syntax:
#Union[int,None]
#This is a change in the newer Python, which I don't have yet so I put 
# in this hack and can change Python version later 
from typing import Union


class AsvRelativeAbundanceBase(BaseModel):
    id: int
    asv_metadata_id: int
    asv_sample_id: int

    class Config:
        orm_mode = True


class AsvRelativeAbundanceCreate(AsvRelativeAbundanceBase):
    pass


class AsvRelativeAbundance(AsvRelativeAbundanceBase):
    abundance: Union[float, None] #KL messing around
    


class AsvMetadataBase(BaseModel):
    id: int

    class Config:
        orm_mode = True


class AsvMetadataCreate(AsvMetadataBase):
    pass


class AsvMetadata(AsvMetadataBase):
    name: str
    sequence: str
    tax_kingdom: Union[str, None] = Field(
        default=None, title="tax_kingdom", max_length=300
    )
    tax_phylum: Union[str ,None] = Field(
        default=None, title="tax_phylum", max_length=300
    )
    tax_class: Union[str ,None] = Field(
        default=None, title="tax_class", max_length=300
    )
    tax_order: Union[str ,None] = Field(
        default=None, title="tax_order", max_length=300
    )
    tax_family: Union[str ,None] = Field(
        default=None, title="tax_family", max_length=300
    )
    tax_genus: Union[str ,None] = Field(
        default=None, title="tax_genus", max_length=300
    )
    tax_comboname: Union[str, None] = Field(
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
    data_type:  Union[str, None]
    data_url: Union[str, None]
    sample_name: Union[str, None]
    fwd_primer: Union[str, None]
    rev_primer: Union[str, None]
    dada2name: Union[str, None] = Field(
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
    old_bottle_id: Union[str, None]
    bottle_id: Union[int , None]
    location_gps_lat: Union[float, None]
    location_gps_long: Union[float, None]
    date_time_triggered: Union[datetime.datetime , None]
    depth_triggered: Union[float, None]
    nominal_depth: Union[float, None]
    temperature: Union[float, None]


class CastBase(BaseModel):
    cast_number:Union[int , None]
    cast_date: Union[datetime.datetime , None]
    mixed_layer_depth_value: Union[float, None]
    mixed_layer_depth_method: Union[str, None] = Field(default='dens_T2',
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
    departure_date: Union[datetime.datetime , None]
    return_date: Union[datetime.datetime , None]
    target_lat: Union[float, None]
    target_long: Union[float, None]
    station: Union[str, None]
    cruise_id: Union[str, None]
    program: Union[str, None]



class CruiseCreate(CruiseBase):
    pass


class Cruise(CruiseBase):
    id: int
    casts: list[Cast] = []

    class Config:
        orm_mode = True


