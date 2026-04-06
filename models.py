from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import relationship

'''
Setting up the models to use with the BIOS-SCOPE dataset
Krista Longnecker, 6 April 2026
'''

class Base(DeclarativeBase):
    pass

# define the classes
class DiscreteInfo(Base):
    __tablename__ = 'discrete'
    id = Column(Integer, primary_key=True, index=True)
    bottleID = Column(String)
    cruise = Column(String)
    cast = Column(String)
    niskin = Column(String)
    yyyymmdd = Column(String)
    nominalDepth = Column(String)
    V1V2data = Column(String)
    V4data = Column(String)
    mtabData = Column(String)
    mtabDataUntargeted = Column(String)
    
    #need this next row to get the nice output (other get a generic thing ?: <__main__.DiscreteInfo object at 0x000001A3FC7A0F70>)
    def __repr__(self):
        return f"<DiscreteInfo(bottleID='{self.bottleID}', cruise='{self.cruise}')>"


class SeqInfoV1V2(Base):
    __tablename__ = 'sequencingV1V2'
    id = Column(Integer, primary_key=True, index=True)
    bottleID = Column(String)
    cast = Column(String)
    NominalDepth = Column(String)
    filename = Column(String)
    V1V2data = Column(String)
    #not sure how to do this next bit yet
    #casts = relationship('Cast', back_populates='cruise')
    
    def __repr__(self):
        return f"<SeqInfoV1V2(bottleID='{self.bottleID}', filename='{self.filename}', V1V2data ='{self.V1V2data}')>"
    
class SeqInfoV4(Base):
    __tablename__ = 'sequencingV4'
    id = Column(Integer, primary_key=True, index=True)
    bottleID = Column(String)
    cast = Column(String)
    NominalDepth = Column(String)
    filename = Column(String)
    V4data = Column(String)
    #not sure how to do this next bit yet
    #casts = relationship('Cast', back_populates='cruise')
    
    def __repr__(self) -> str:
        return f"SeqInfoV4(id={self.id!r}, name={self.bottleID!r}, V4data={self.V4data!r})"
  
   
class CyverseInfo(Base):
    __tablename__ = 'cyverse'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)  
    def __repr__(self) -> str:
        return f"index(id={self.id!r}, filename={self.filename!r})"
    
    
class MetaboliteInfo(Base):
    __tablename__ = 'metabolites'
    id = Column(Integer, primary_key=True, index=True)
    bottleID = Column(String)
    dataSource = Column(String)
    
    def __repr__(self) -> str:
        return f"MetaboliteInfo(id={self.id!r}, bottleID={self.bottleID!r}, dataSource={self.dataSource!r})"


class MtabUntargetedInfo(Base):
    __tablename__ = 'metabolitesUntargeted'
    id = Column(Integer, primary_key=True, index=True)
    bottleID = Column(String)
    dataSource = Column(String)
    
    def __repr__(self) -> str:
        return f"MtabUntargetedInfo(id={self.id!r}, bottleID={self.bottleID!r}, dataSource={self.dataSource!r})"
