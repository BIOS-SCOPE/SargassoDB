from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import relationship
#these nexxt two are updated (new syntax in SQLalchemy)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

'''
Setting up the models to use with the BIOS-SCOPE dataset
Krista Longnecker, 6 April 2026
Krista Longnecker, 27 June 2026
Krista Longnecker, 31 August 2026 --> ready to make this a relational database with defined links
'''

class Base(DeclarativeBase):
    pass

# define the classes  
class DiscreteInfo(Base):
    __tablename__ = 'discrete'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Core fields from the file 
    bottleID: Mapped[str] = mapped_column(String)
    cruise: Mapped[str] = mapped_column(String)
    cast: Mapped[str] = mapped_column(String)
    niskin: Mapped[str] = mapped_column(String)
    yyyymmdd: Mapped[str] = mapped_column(String)
    nominalDepth: Mapped[str] = mapped_column(String)
    
    # # also add in empty columns for the pieces I am adding based on matches (e.g., not just what is in the discrete file)
    # # I think these can be linked from other places and found by query (8/31/2026...working)
    # sType: Mapped[Optional[str]] = mapped_column(String, default=None)
    # location: Mapped[Optional[str]] = mapped_column(String, default=None)
    # status: Mapped[Optional[str]] = mapped_column(String, default=None)
    # extracted: Mapped[Optional[str]] = mapped_column(String, default=None)
    # analyst1: Mapped[Optional[str]] = mapped_column(String, default=None)
    # V1V2data: Mapped[Optional[str]] = mapped_column(String, default=None)
    # V4_16Sdata: Mapped[Optional[str]] = mapped_column(String, default=None)
    # V4_18Sdata: Mapped[Optional[str]] = mapped_column(String, default=None)
    # mtabData: Mapped[Optional[str]] = mapped_column(String, default=None)
    # mtabDataUntargeted: Mapped[Optional[str]] = mapped_column(String, default=None)  
    
    # =========================================================================
    # RELATIONSHIPS (think of these as shortcuts in Python)
    # =========================================================================
    # 1-to-1 relationship with SeqInfoBasics
    seq_basics: Mapped[Optional["SeqInfoBasics"]] = relationship(back_populates="parent_discrete")
    
    # 1-to-Many relationship (Assuming a bottle could have multiple V4 rows): need list to get multiple rows
    v4_16s_runs: Mapped[list["SeqInfoV4_16S"]] = relationship("SeqInfoV4_16S", back_populates="parent_discrete")   
    v4_18s_runs: Mapped[list["SeqInfoV4_18S"]] = relationship("SeqInfoV4_18S",back_populates="parent_discrete")
    v1v2_runs: Mapped[list["SeqInfoV1V2"]] = relationship("SeqInfoV1V2",back_populates="parent_discrete")
    
    #need this next row to get the nice output and not generic text
    def __repr__(self):
        return f"<DiscreteInfo(bottleID='{self.bottleID}', cruise='{self.cruise}')>"

class SeqInfoBasics(Base):
    __tablename__ = 'sequencingBasics'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"),default=None)
    sType: Mapped[Optional[str]] = mapped_column(String, default=None)
    location: Mapped[Optional[str]] = mapped_column(String, default=None)
    status: Mapped[Optional[str]] = mapped_column(String, default=None)
    extracted: Mapped[Optional[str]] = mapped_column(String, default=None)
    analyst1: Mapped[Optional[str]] = mapped_column(String, default=None)
    
    # Trying this : Back-populate link back to DiscreteInfo
    parent_discrete: Mapped[Optional["DiscreteInfo"]] = relationship("DiscreteInfo",back_populates="seq_basics")
    
    def __repr__(self):
        return f"<SeqInfo_basics(bottleID='{self.bottleID}', extracted='{self.extracted}', Analyst1 ='{self.analyst1}')>"

class SeqInfoV4_16S(Base):
    __tablename__ = 'sequencingV4_16S'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"), default=None)
    cast: Mapped[Optional[str]] = mapped_column(String, default=None)
    NominalDepth: Mapped[Optional[str]] = mapped_column(String, default=None)
    filename: Mapped[Optional[str]] = mapped_column(String, default=None)
    V4_16Sdata: Mapped[Optional[str]] = mapped_column(String, default=None)
    # set the relationship to DiscreteInfo:
    parent_discrete: Mapped[list["DiscreteInfo"]] = relationship("DiscreteInfo",back_populates="v4_16s_runs")

    def __repr__(self) -> str:
        return f"SeqInfoV4_16S(id={self.id!r}, name={self.bottleID!r}, V4_16Sdata={self.V4_16Sdata!r})"
    
class SeqInfoV1V2(Base):
    __tablename__ = 'sequencingV1V2'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"), default=None)
    cast: Mapped[Optional[str]] = mapped_column(String, default=None)
    NominalDepth: Mapped[Optional[str]] = mapped_column(String, default=None)
    filename: Mapped[Optional[str]] = mapped_column(String, default=None)
    V1V2data: Mapped[Optional[str]] = mapped_column(String, default=None)
    parent_discrete: Mapped[list["DiscreteInfo"]] = relationship("DiscreteInfo",back_populates="v1v2_runs")
    
    def __repr__(self):
        return f"<SeqInfoV1V2(bottleID='{self.bottleID}', filename='{self.filename}', V1V2data ='{self.V1V2data}')>"

class SeqInfoV4_18S(Base):
    __tablename__ = 'sequencingV4_18S'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bottleID: Mapped[Optional[str]] = mapped_column(String,ForeignKey("discrete.bottleID"), default=None)
    cast: Mapped[Optional[str]] = mapped_column(String, default=None)
    NominalDepth: Mapped[Optional[str]] = mapped_column(String, default=None)
    filename: Mapped[Optional[str]] = mapped_column(String, default=None)
    V4_18Sdata: Mapped[Optional[str]] = mapped_column(String, default=None)
    parent_discrete: Mapped[list["DiscreteInfo"]] = relationship("DiscreteInfo",back_populates="v4_18s_runs")
    
    def __repr__(self) -> str:
        return f"SeqInfoV4_18S(id={self.id!r}, name={self.bottleID!r}, V4_18Sdata={self.V4_18Sdata!r})"
        

class SeqInfoNCBIinhouse(Base):
    __tablename__ = 'SeqInfoNCBIinhouse' #this is the parent for NCBI
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    #join the ncbi child (the online NCBI information) on this next field 
    #biosample: Mapped[str] = mapped_column(String, unique = True, index=True) #cannot use, have issues
    # biosample: Mapped[Optional[str]] = mapped_column(String, nullable=True, default = None)
    biosample: Mapped[Optional[str]] = mapped_column(String, nullable=True, default = None)
    
    cruise5: Mapped[Optional[str]] = mapped_column(String, default=None)
    sampleV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    sraV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    seqV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    sampleV416s: Mapped[Optional[str]] = mapped_column(String, default=None)
    sraV416s: Mapped[Optional[str]] = mapped_column(String, default=None)
    seqV416s: Mapped[Optional[str]] = mapped_column(String, default=None)
    firstReference: Mapped[Optional[str]] = mapped_column(String, default=None)
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"), default=None)
    
    #this is the parent, define the shortcut to the child
    child_ncbi: Mapped[list["SeqInfoNCBIonline"]] = relationship(
        "SeqInfoNCBIonline", 
        primaryjoin="SeqInfoNCBIonline.biosample== SeqInfoNCBIinhouse.biosample",
        foreign_keys="[SeqInfoNCBIonline.biosample]",
        uselist = True,
        back_populates = 'parent_ncbi'
    )
    
    def __repr__(self) -> str:
        return f"SeqInfoNCBIonline(id={self.id!r}, cruise5={self.cruise5!r})"
    
        
class SeqInfoNCBIonline(Base):
    __tablename__ = 'SeqInfoNCBIonline' #this is the child for NCBI
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    biosample: Mapped[Optional[str]] = mapped_column(String, ForeignKey("SeqInfoNCBIinhouse.biosample"),default=None)
    sample: Mapped[Optional[str]] = mapped_column(String, default = None)   

    #this should be one-to-one, though I suspect it will not be...let's see what happens; define link to the parent
    parent_ncbi: Mapped["SeqInfoNCBIinhouse"] = relationship(
        "SeqInfoNCBIinhouse", 
        primaryjoin="SeqInfoNCBIonline.biosample == SeqInfoNCBIinhouse.biosample",
        back_populates="child_ncbi"
    )
    
    def __repr__(self) -> str:
        return f"SeqInfoNCBIonline(id={self.id!r}, sample={self.sample!r}, biosample={self.biosample!r})"
    
    

class SeqInfoLTTs1(Base):
    __tablename__ = 'SeqInfoLTTs1'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    biosample: Mapped[Optional[str]] = mapped_column(String, default=None)
    sraV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    year: Mapped[Optional[str]] = mapped_column(String, default=None)
    month: Mapped[Optional[str]] = mapped_column(String, default=None)
    depth: Mapped[Optional[str]] = mapped_column(String, default=None)
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"),default=None)
    
    def __repr__(self) -> str:
        return f"SeqInfoLTTs1(id={self.id!r}, bottleID={self.bottleID!r}, biosample={self.biosample!r})"
    
class SeqInfoLTTdeep(Base):
    __tablename__ = 'SeqInfoLTTdeep'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sample: Mapped[Optional[str]] = mapped_column(String, default=None)
    biosample: Mapped[Optional[str]] = mapped_column(String, default=None)
    sraV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    year: Mapped[Optional[str]] = mapped_column(String, default=None)
    month: Mapped[Optional[str]] = mapped_column(String, default=None)
    depth: Mapped[Optional[str]] = mapped_column(String, default=None)
    bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"),default=None)
    
    def __repr__(self) -> str:
        return f"SeqInfoLTTdeep(id={self.id!r}, bottleID={self.bottleID!r}, biosample={self.biosample!r})"
    
class NCBIunreleased(Base):
    __tablename__ = 'NCBIunreleased'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    biosample: Mapped[Optional[str]] = mapped_column(String, ForeignKey("SeqInfoNCBIinhouse.biosample"), default=None)
    sraV1V2: Mapped[Optional[str]] = mapped_column(String, default=None)
    title: Mapped[Optional[str]] = mapped_column(String, default=None)
    
    
    #the NCBI unreleased will not be in the discrete file as many (all?) are older BATS samples
    #bottleID: Mapped[Optional[str]] = mapped_column(String, ForeignKey("discrete.bottleID"),default=None)
    
    def __repr__(self) -> str:
        return f"NCBIunreleased(id={self.id!r}, biosample={self.biosample!r})"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
class CyverseInfo(Base):
    __tablename__ = 'cyverse'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String)  
    source: Mapped[str] = mapped_column(String)
    V4_16S_found: Mapped[Optional[str]] = mapped_column(String, default=None)
    V4_18S_found: Mapped[Optional[str]] = mapped_column(String, default=None)
    V1V2_found: Mapped[Optional[str]] = mapped_column(String, default=None)
    
    def __repr__(self) -> str:
        return f"index(id={self.id!r}, filename={self.filename!r})"
    
    
class MetaboliteInfo(Base):
    __tablename__ = 'metabolites'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bottleID: Mapped[str] = mapped_column(String, default=None)
    dataSource: Mapped[str] = mapped_column(String)
    
    def __repr__(self) -> str:
        return f"MetaboliteInfo(id={self.id!r}, bottleID={self.bottleID!r}, dataSource={self.dataSource!r})"


class MtabUntargetedInfo(Base):
    __tablename__ = 'metabolitesUntargeted'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bottleID: Mapped[str] = mapped_column(String, default=None)
    dataSource: Mapped[str] = mapped_column(String)
    
    def __repr__(self) -> str:
        return f"MtabUntargetedInfo(id={self.id!r}, bottleID={self.bottleID!r}, dataSource={self.dataSource!r})"
