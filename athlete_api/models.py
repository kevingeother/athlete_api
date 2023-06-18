from enum import Enum
from typing import Any, Dict, Optional, Tuple

from sqlmodel import Field, SQLModel


#add class descriptions
class Seasons(str, Enum):
    SUMMER = 'summer'
    WINTER = 'winter'
    UNION = 'union'

class Medals(str, Enum):
    GOLD = 'Gold'
    SILVER = 'Silver'
    BRONZE = 'Bronze'

class RegionBase(SQLModel):
    noc: str
    region: Optional[str]
    notes: Optional[str] = None

class RegionUpdate(RegionBase):
    noc: Optional[str]
    region: Optional[str]
    notes: Optional[str] = None

class Region(RegionBase, table=True):
    __tablename__ = 'regions'
    noc: Optional[str] = Field(default=None, primary_key=True)


class AthleteBase(SQLModel):
    name: str
    sex: str
    age: float
    team: str
    noc: str = Field(foreign_key="regions.noc")
    games: str
    year: int
    season: str
    city: str
    sport: str
    event: str
    medal: Optional[Medals] = None

class AthleteUpdate(AthleteBase):
    name: Optional[str]
    sex: Optional[str]
    age: Optional[float]
    team: Optional[str]
    noc: Optional[str] = Field(foreign_key="regions.noc")
    games: Optional[str]
    year: Optional[int]
    season: Optional[str]
    city: Optional[str]
    sport: Optional[str]
    event: Optional[str]
    medal: Optional[Medals] = None

class AthleteSummer(AthleteBase,  table=True):
    __tablename__ = 'athletes_summer'
    id: Optional[int] = Field(default=None, primary_key=True)


class AthleteWinter(AthleteBase,  table=True):
    __tablename__ = 'athletes_winter'
    id: Optional[int] = Field(default=None, primary_key=True)
