"""
Model classes for postgresql db
"""
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
  """Base model for regions

  Args:
      SQLModel (_type_): _description_
  """
  noc: str
  region: Optional[str]
  notes: Optional[str] = None

class RegionUpdate(RegionBase):
  """Update model for regions

  Args:
      RegionBase (_type_): inherits from RegionBase
  """
  noc: Optional[str]
  region: Optional[str]
  notes: Optional[str] = None

class Region(RegionBase, table=True):
    __tablename__ = 'regions'
    noc: Optional[str] = Field(default=None, primary_key=True)


class AthleteBase(SQLModel):
  """Base model for athletes

  Args:
      SQLModel (_type_): _description_
  """
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
  """Update model for athletes

  Args:
      RegionBase (_type_): inherits from AthleteBase
  """
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
  """Custom model for Summer table with tablename

  Args:
      AthleteBase (_type_): Inherits from AthleteBase
      table (bool, optional):  Defaults to True.
  """
  __tablename__ = 'athletes_summer'
  id: Optional[int] = Field(default=None, primary_key=True)


class AthleteWinter(AthleteBase,  table=True):
  """Custom model for Winter table with tablename
    
  Args:
      AthleteBase (_type_): Inherits from AthleteBase
      table (bool, optional):  Defaults to True.
  """
  __tablename__ = 'athletes_winter'
  id: Optional[int] = Field(default=None, primary_key=True)
