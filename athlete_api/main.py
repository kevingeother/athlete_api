import os
from collections import defaultdict
from itertools import groupby

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine, inspect, select, union

from .models import (AthleteBase, AthleteSummer, AthleteUpdate, AthleteWinter,
                     Region, RegionBase, RegionUpdate, Seasons)
from .services import connect
from .utils import add_where, verify_params

# database_url = "postgresql://postgres:123@db:5432/athletes"
# engine = create_engine(database_url)
engine = connect(filename=os.getenv('FILE_NAME'), section=os.getenv('SECTION_NAME'), echo=True)

#debug
table_names = inspect(engine)
print(table_names.get_table_names())

#We create an instance of FastAPI
app = FastAPI()

# We define authorizations for middleware components
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# today = datetime.date.today()
# year = today.year


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


@app.get("/")
async def read_root():
    return {"start":"API to query athletes/countries in Olympics"}


#add try/except
# search in regions and notes eg: newfoundland
# add rate limit https://sqlmodel.tiangolo.com/tutorial/fastapi/limit-and-offset/
# error documentation 400
@app.get("/country/{country}", response_model= dict)
def get_country_data(country: str,
                 sport: str = None,
                 start_date: int = None,
                 end_date: int = None,
                 detail: bool = False,
                 season: Seasons = Seasons.UNION,
                 exact: bool = True):
    # local = locals()
    try:
        verify = verify_params(country, sport, start_date, end_date)
        assert verify is True
    except (AssertionError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    with Session(engine) as session:
        statement_1 = select(AthleteSummer, Region.region, Region.notes)\
                        .where(AthleteSummer.noc == Region.noc)
        statement_1 = add_where(statement=statement_1,
                                clauses=[
                                    ('region', country, 'equal' if exact else 'contain'),
                                    ('sport', sport, 'equal'),
                                    ('year', start_date, 'gte'),
                                    ('year', end_date, 'lte')]
                                )
        statement_2 = select(AthleteWinter, Region.region, Region.notes)\
                        .where(AthleteWinter.noc == Region.noc)
        statement_2 = add_where(statement=statement_2,
                                clauses=[
                                    ('region', country, 'equal' if exact else 'contain'),
                                    ('sport', sport, 'equal'),
                                    ('year', start_date, 'gte'),
                                    ('year', end_date, 'lte')]
                                )

        if season == Seasons.SUMMER:
            statement = union(statement_1, statement_1)
        elif season == Seasons.WINTER:
            statement = union(statement_2, statement_2)
        elif season == Seasons.UNION:
            statement = union(statement_1, statement_2)

        athletes = session.exec(statement).fetchall()
        #adding secondary key to ensure ordering for next step groupby
        sorted_athletes = sorted(athletes, 
                                 key=lambda x: (x.region.lower().find(country), x.region, x.year))
        grouped_data = groupby(sorted_athletes, key=lambda x: x.region)
        result = defaultdict(lambda: defaultdict())
        for country_name, group in grouped_data:
            group = list(group)
            result[country_name]['total_entries'] = len(group)
            result[country_name]['unique_participants'] = len({g.name for g in group})
            result[country_name]['medal_count'] = {
                'total': len([g for g in group if g.medal]),
                'gold':len([g for g in group if g.medal=='Gold']),
                'silver':len([g for g in group if g.medal=='Silver']),
                'bronze':len([g for g in group if g.medal=='Bronze']),
                }# if group else 0
            result[country_name]['games'] = sorted({g.games for g in group})
            if detail:
                result[country_name]['entries'] = group
        return result

#TODO 
# union winter: done
# fix return: done
# custom where functions: done
# sort by diff keys param
@app.get("/noc/{noc}", response_model= dict)
def get_noc_data(noc: str,
                 sport: str = None,
                 start_date: int = None,
                 end_date: int = None,
                 detail: bool = False,
                 season: Seasons = Seasons.UNION):
    try:
        verify = verify_params(noc, sport, start_date, end_date)
        assert verify is True
    except (AssertionError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    with Session(engine) as session:
        statement_1 = select(AthleteSummer)
        statement_1 = add_where(statement=statement_1,
                                clauses=[
                                    ('noc', noc, 'equal'),
                                    ('sport', sport, 'equal'),
                                    ('year', start_date, 'gte'),
                                    ('year', end_date, 'lte')])
        statement_2 = select(AthleteWinter)
        statement_2 = add_where(statement=statement_2,
                                clauses=[
                                    ('noc', noc, 'equal'),
                                    ('sport', sport, 'equal'),
                                    ('year', start_date, 'gte'),
                                    ('year', end_date, 'lte')])

        if season == Seasons.SUMMER:
            statement = union(statement_1, statement_1)
        elif season == Seasons.WINTER:
            statement = union(statement_2, statement_2)
        elif season == Seasons.UNION:
            statement = union(statement_1, statement_2)

        athletes = session.exec(statement).fetchall()
        #adding secondary key to ensure ordering for next step groupby
        sorted_athletes = sorted(athletes, key=lambda x: x.year)

        grouped_data = groupby(sorted_athletes, key=lambda x: x.year)
        result = defaultdict(lambda: defaultdict())
        for year, group in grouped_data:
            group = list(group)
            result[year]['season'] = {g.season for g in group}
            result[year]['total_entries'] = len(group)
            result[year]['unique_participants'] = len({g.name for g in group}) if group else 0
            result[year]['medal_count'] = {
                'total': len([g for g in group if g.medal]),
                'gold':len([g for g in group if g.medal=='Gold']),
                'silver':len([g for g in group if g.medal=='Silver']),
                'bronze':len([g for g in group if g.medal=='Bronze']),
                }
            if detail:
                result[year]['entries'] = group
        return result


#TODO
# correct season union
# union winter :done
# add return params? - struct mess
# add  games, country: done
# add_medal : done
@app.get("/athletes/{athlete_name}", response_model=dict)
def get_athlete_data(athlete_name: str,
                    #  medal_winner:bool = False, 
                     exact: bool = False,
                     detail: bool = False,
                     season: Seasons = Seasons.UNION,
                    #  sort:str = 'name'
                    ):
    # local = locals()
    with Session(engine) as session:
        statement_1 = select(AthleteSummer)
        statement_1 = add_where(statement=statement_1,
                                clauses=[
                                    ('name', athlete_name, 'equal' if exact else 'contain'),
                                    # ('medal', medal_winner, 'non_null' if medal_winner else None)
                                    ])
        statement_2 = select(AthleteWinter)
        statement_2 = add_where(statement=statement_2,
                                clauses=[('name', athlete_name, 'equal' if exact else 'contain')])

        if season == Seasons.SUMMER:
            statement = union(statement_1, statement_1)
        elif season == Seasons.WINTER:
            statement = union(statement_2, statement_2)
        elif season == Seasons.UNION:
            statement = union(statement_1, statement_2)

        athletes = session.exec(statement).fetchall()
        sorted_athletes = sorted(athletes,
                                 key=lambda x: (x.name.lower().find(athlete_name), x.name, x.year))

        ## group by
        grouped_data = groupby(sorted_athletes, key=lambda x: x.name)
        result = defaultdict(lambda: defaultdict())
        for name, group in grouped_data:
            group = list(group)
            result[name]['medal_count'] = len([g for g in group if g.medal])
            result[name]['teams'] = sorted({g.team for g in group})
            result[name]['games'] = sorted({g.games for g in group})
            result[name]['sports'] = sorted({g.sport for g in group})
            if detail:
                result[name]['entries'] = group
        return result


#propogate errors
#return types
@app.post("/add_athlete/")
def add_athlete(*, session: Session = Depends(get_session), athlete: AthleteBase):
    season = athlete.season.lower()
    match(season):
        case Seasons.SUMMER:
            db_athlete = AthleteSummer.from_orm(athlete)
        case Seasons.WINTER:
            db_athlete = AthleteWinter.from_orm(athlete)
        case _:
            raise HTTPException(status_code=422, detail="Invalid Season. 'Winter' or 'Summer'")
    try:
        session.add(db_athlete)
        session.commit()
        session.refresh(db_athlete)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return db_athlete


#propogate errors
#return types
# add doc for 404 error
# better error handling psycopg2 https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
@app.patch("/update_athlete/{athlete_id}")
def update_athlete(*, session: Session = Depends(get_session), athlete_id: int, athlete_update: AthleteUpdate):
    db_athlete = session.get(AthleteSummer, athlete_id)
    if not db_athlete:
        db_athlete = session.get(AthleteWinter, athlete_id)
    if not db_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for field, value in athlete_update.dict(exclude_unset=True).items():
        setattr(db_athlete, field, value)
    try:
        session.add(db_athlete)
        session.commit()
        session.refresh(db_athlete)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return db_athlete


@app.delete("/delete_athlete/{athlete_id}")
def delete_athlete(*, session: Session = Depends(get_session), athlete_id: int):
    db_athlete = session.get(AthleteSummer, athlete_id)
    if not db_athlete:
        db_athlete = session.get(AthleteWinter, athlete_id)
    if not db_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    session.delete(db_athlete)
    session.commit()
    return {"Deleted": True}


#propogate errors
#return types
@app.post("/add_region/", response_model=Region)
def add_region(*, session: Session = Depends(get_session), region: RegionBase):
    db_region = Region.from_orm(region)
    try:
        session.add(db_region)
        session.commit()
        session.refresh(db_region)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return db_region


@app.patch("/update_region/{noc}", response_model=Region)
def update_region(*, session: Session = Depends(get_session), noc: str, region_update:RegionUpdate):
    db_region = session.get(Region, noc)
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")
    for field, value in region_update.dict(exclude_unset=True).items():
        setattr(db_region, field, value)
    try:
        session.commit()
        session.refresh(db_region)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return db_region


@app.delete("/delete_region/{noc}")
def delete_region(*, session: Session = Depends(get_session), noc: str):
    db_region = session.get(Region, noc)
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")

    session.delete(db_region)
    session.commit()
    return {"Deleted": True}
