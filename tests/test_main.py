"""
Pytest functions
"""

import pytest
import requests
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi import Depends, FastAPI, HTTPException

from athlete_api.models import (AthleteBase, AthleteSummer, AthleteWinter,
                              Region, RegionBase, RegionUpdate, Seasons)
from athlete_api.main import app
                            #   get_session)
from athlete_api.services import connect

# app = FastAPI()

@pytest.fixture(name="session")  # , scope='session'
def session_fixture():
    # database_url = "postgresql://postgres:123@localhost:5432/athletes_test"
    # engine = create_engine(database_url, echo=False)
    engine = connect(filename='athlete_api/database.ini', section='postgresql_test',
                     echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        region = Region(noc="NO1", region="Test Region 1", notes="Test Notes 1")
        session.add(region)
        session.flush()
        yield session
        session.delete(region)
        session.flush()
        session.close()


@pytest.fixture(name="client", scope="function")  # , scope='session'
def client_fixture():
    client = TestClient(app)
    yield client
    client.close()


def test_add_region(client: TestClient):
    """
     Test adding a region to an existing region.
     
     Args:
     	 client: The client to use for the test ( Required)
    """
    response = client.post(
        "/add_region/",
        json={"noc": "NO2", "region": "Test Region 2", "notes": "Test Notes 2"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["noc"] == "NO2"
    assert data["region"] == "Test Region 2"
    assert data["notes"] == "Test Notes 2"


# ideally have Region limited to 3 char with custom class
def test_add_region_invalid(client: TestClient):
    """
     Test adding a region that is invalid. Should return 422.
     
     Args:
     	 client: The client to use for the test ( Required)
    """
  # noc None. Another test needed for 3 length
    response = client.post(
        "/add_region/",
        json={
            "noc": None,
        },
    )
    assert response.status_code == 422


def test_update_region(session: Session, client: TestClient):
    """
     Test updating a region. 
     
     Args:
     	 session: The session to use for the test ( Required)
     	 client: The client to use for the test ( Required)
    """
    region = Region(noc="NO2", region="Test Region 2", notes="Test Notes 2")
    session.add(region)
    response = client.patch(
        f"/update_region/{region.noc}",
        json={"region": "Test Region 2 Updated", "notes": None},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["noc"] == "NO2"
    assert data["region"] == "Test Region 2 Updated"
    assert data["notes"] is None


def test_update_region_invalid(session: Session, client: TestClient):
    """
     Test update_region with invalid noc. Expect 422.
     
     Args:
     	 session: The session to use for the test ( Required)
     	 client: The client to use for the test ( Required)
    """
    # noc None. Another test needed for 3 length
    region = Region(noc="NO2", region="Test Region 2", notes="Test Notes 2")
    session.add(region)
    response = client.patch(
        f"/update_region/{region.noc}",
        json={"noc": None, "region": "Test Region 2 Updated", "notes": None},
    )
    assert response.status_code == 422


def test_update_region_incorrect(session: Session, client: TestClient):
    """
     Test that an incorrect noc will return 404.
     
     Args:
     	 session: The session to use for the test ( Required)
     	 client: The client to use for the test ( Required)
    """
    # noc incorrect.
    region = Region(noc="NO2", region="Test Region 2", notes="Test Notes 2")
    session.add(region)
    response = client.patch(
        "/update_region/A01",
        json={"noc": "NO2", "region": "Test Region 2 Updated", "notes": None},
    )
    assert response.status_code == 404


def test_delete_region(session: Session, client: TestClient):
    """
     Test deleting a region.
     
     Args:
     	 session: The session to use for the test ( Required)
     	 client: The client to use for the test ( Required)
    """
    region = Region(noc="NO2", region="Test Region 2", notes="Test Notes 2")
    session.add(region)
    response = client.delete(f"/delete_region/{region.noc}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"Deleted": True}


def test_delete_region_incorrect(session: Session, client: TestClient):
    """
     Test that a DELETE request with incorrect noc fails.
     
     Args:
     	 session: The session to use for the test ( Required)
     	 client: The client to use for the test ( Required)
    """
    # noc incorrect
    region = Region(noc="NO2", region="Test Region 2", notes="Test Notes 2")
    session.add(region)
    response = client.delete("/delete_region/AO3")
    assert response.status_code == 404


def test_add_athlete(client: TestClient):
    """
     Test adding a athlete to the database
     
     Args:
     	 client: The client to use for the test ( Required)
    """
    athlete = AthleteBase(
        name="Test Name",
        sex="M",
        age=25.0,
        team="Test Team",
        noc="NO1",
        games="Test Games 2020",
        year=2020,
        season="Summer",
        city="Test City",
        sport="Test Sport",
        event="Test Event",
        medal="Gold",
    )
    client.post(
        "/add_region/",
        json={"noc": "NO1", "region": "Test Region 2", "notes": "Test Notes 2"},
    )
    response = client.post(
        "/add_athlete/",
        json={
            "name": "Test Name",
            "sex": "M",
            "age": 25.0,
            "team": "Test Team",
            "noc": "NO1",
            "games": "Test Games 2020",
            "year": 2020,
            "season": "Summer",
            "city": "Test City",
            "sport": "Test Sport",
            "event": "Test Event",
            "medal": "Gold"
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Name"
    assert data["sex"] == "M"
    assert data["age"] == 25.0
    assert data["team"] == "Test Team"
    assert data["noc"] == "NO1"
    assert data["games"] == "Test Games 2020"
    assert data["year"] == 2020
    assert data["season"] == "Summer"
    assert data["city"] == "Test City"
    assert data["sport"] == "Test Sport"
    assert data["event"] == "Test Event"
    assert data["medal"] == "Gold"


def test_add_athlete_incomplete(client: TestClient):
    """
     Test adding an Athlete with incomplete data. 
     
     Args:
     	 client: The client to use
    """
    # Only one field
    response = client.post("/add_athlete/", json={"name": "Test Name"})
    assert response.status_code == 422


def test_add_athlete_invalid(client: TestClient):
    """
     Test adding an invalid ahlete.
     
     Args:
      session: The session to use for the test ( Required)
    """
    # season invalid type.
    response = client.post(
        "/add_athlete/",
        json={
            "name": "Test Name",
            "sex": "M",
            "age": 25.0,
            "team": "Test Team",
            "noc": "NO1",
            "games": "Test Games 2020",
            "year": 2020,
            "season": "Spring",
            "city": "Test City",
            "sport": "Test Sport",
            "event": "Test Event",
            "medal": "Gold",
        },
    )
    assert response.status_code == 422


# erroneous
# def test_update_athlete(session: Session, client: TestClient):
#     client.post("/add_athlete/", json={
#                             'id': 1,
#                             "name": "Test Name",
#                             "sex": "M",
#                             "age": 25,
#                             "team": "Test Team",
#                             "noc": "NO1",
#                             "games": "Test Games 2020",
#                             "year": 2020,
#                             "season": "Summer",
#                             "city": "Test City",
#                             "sport": "Test Sport",
#                             "event": "Test Event",
#                             "medal": "Gold"
#                             })
#     db_athlete = client.get("/athletes/Test Name")
#     print("\n\nhere",db_athlete.json()['Test Name'])

#     response = client.patch("/update_athlete/1",json={"name": "Test Name Update"})
#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == "Test Name Update"
#     assert data["sex"] == "M"
#     assert data["age"] == 25.0
#     assert data["team"] == "Test Team"
#     assert data["noc"] == "NO1"
#     assert data["games"] == "Test Games 2020"
#     assert data["year"] == 2020
#     assert data["season"] == "Summer"
#     assert data["city"] == "Test City"
#     assert data["sport"] == "Test Sport"
#     assert data["event"] == "Test Event"
#     assert data["medal"] == "Gold"


def test_update_athlete_invalid(session: Session, client: TestClient):
    """
     Test updating an invalid athlete.
     
     Args:
      session: The session to use for the test ( Required)
      client: The client to use for the test ( Required)
    """
    athlete = AthleteBase(
        name="Test Name",
        sex="M",
        age=25.0,
        team="Test Team",
        noc="NO1",
        games="Test Games 2020",
        year=2020,
        season="Summer",
        city="Test City",
        sport="Test Sport",
        event="Test Event",
        medal="Gold",
    )
    match (athlete.season.lower()):
        case Seasons.SUMMER:
            db_athlete = AthleteSummer.from_orm(athlete)
        case Seasons.WINTER:
            db_athlete = AthleteWinter.from_orm(athlete)

    session.add(db_athlete)
    session.flush()
    session.refresh(db_athlete)

    response = client.patch(
        f"/update_athlete/{db_athlete.id}", json={"age": "Test Name Update"}
    )
    assert response.status_code == 422


def test_update_athlete_incorrect(client: TestClient):
    """
     Update Athlete with incorrect name. This should fail with 404.
     
     Args:
      session: The session to use for the test ( Required)
      client: The client to use for the test ( Required)
    """
    response = client.patch("/update_athlete/-10", json={"name": "Test Name Update"})
    assert response.status_code == 404


def test_delete_athlete(session: Session, client: TestClient):
    """
     Test deleting an athlete.
     
     Args:
      session: The session to use for the test ( Required)
      client: The client to use for the test ( Required)
    """
    athlete = AthleteBase(
        name="Test Name",
        sex="M",
        age=25.0,
        team="Test Team",
        noc="NO1",
        games="Test Games 2020",
        year=2020,
        season="Summer",
        city="Test City",
        sport="Test Sport",
        event="Test Event",
        medal="Gold",
    )
    match (athlete.season.lower()):
        case Seasons.SUMMER:
            db_athlete = AthleteSummer.from_orm(athlete)
        case Seasons.WINTER:
            db_athlete = AthleteWinter.from_orm(athlete)

    session.add(db_athlete)
    session.flush()
    session.refresh(db_athlete)

    response = client.delete(f"/delete_athlete/{db_athlete.id}")
    data = response.json()

    assert response.status_code == 200
    assert data == {"Deleted": True}


def test_delete_athlete_incorrect(client: TestClient):
    """
     Test that an incorrect Athlete can't be deleted. Incorrect Athlete is a non - existent resource and should result in a 404
     
     Args:
      session: The session to use for the test ( Required)
      client: The client to use for the test ( Required)
    """
    response = client.delete("/delete_athlete/-10")
    assert response.status_code == 404


# already covered by assertion in main function
# def test_get_country_data_var1(session:Session, client:TestClient):
#     country_1 = 'Spain'
#     country_2 = None
#     sport_1 = 'Swimming'
#     sport_2 = None
#     start_date: int = None
#     end_date: int = None
#     detail: bool = False
#     season: Seasons = Seasons.SUMMER
#     exact: bool = True
#     verify_1 = verify_params(country_2, sport_1, start_date, end_date)
#     assert isinstance(verify_1, ValueError) is True
#     verify_2 = verify_params(country_1, sport_2, start_date, end_date)
#     assert verify_2 is not True


def test_get_country_data():
    """
     Test route
    """
    response = requests.get(
        "http://localhost:8000/country/fin?sport=judo&detail=false&season=union&exact=false"
    )
    data = response.json()
    assert response.status_code == 200
    assert data == {
        "Finland": {
            "total_entries": 27,
            "unique_participants": 22,
            "medal_count": {
            "total": 0,
            "gold": 0,
            "silver": 0,
            "bronze": 0
            },
            "games": [
            "1972 Summer",
            "1976 Summer",
            "1980 Summer",
            "1984 Summer",
            "1988 Summer",
            "1992 Summer",
            "1996 Summer",
            "2000 Summer",
            "2004 Summer",
            "2008 Summer",
            "2012 Summer",
            "2016 Summer"
            ]
        }
    }


def test_get_noc_data():
    """
    Test route
    """
    response = requests.get(
        "http://127.0.0.1:8000/noc/NFL?start_date=1900&end_date=1910&detail=false&season=union"
    )
    data = response.json()
    assert response.status_code == 200
    assert data == {
        "1904": {
            "season": ["Summer"],
            "total_entries": 1,
            "unique_participants": 1,
            "medal_count": {"total": 0, "gold": 0, "silver": 0, "bronze": 0},
        }
    }


def test_get_athlete_data():
    """
    Test route
    """
    response = requests.get(
        "http://127.0.0.1:8000/athletes/Tester?exact=false&detail=false&season=union"
    )
    data = response.json()
    assert response.status_code == 200
    assert data == {
        "Jan Roger Skyttester": {
            "medal_count": 0,
            "teams": ["Norway"],
            "games": ["1984 Summer"],
            "sports": ["Archery"],
        }
    }
