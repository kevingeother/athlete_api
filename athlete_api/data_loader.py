# import psycopg2
import os
from typing import List

from sqlmodel import Session

from athlete_api.services import connect

os.environ['FILE_NAME'] = './athlete_api/database.ini'
os.environ['SECTION_NAME'] = 'postgresql'

# Connect to PostgreSQL
engine = connect(filename=os.getenv('FILE_NAME'), section=os.getenv('SECTION_NAME'), echo=True)



# conn = psycopg2.connect(
#     host="db",
#     port="5432",
#     dbname='athletes',
#     user="postgres",
#     password="123"
# )

# # Create a cursor object
# cursor = conn.cursor()

# Create sequences and tables
def data_loader(dbName:str = None):

    with Session(engine) as session:
        # Create sequence if it doesn't exist
        sequence_exists= session.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_sequences
                    WHERE sequencename = 'athletes_id_seq'
                )
            """).fetchone()[0]

        create_sequences_query = """
                CREATE SEQUENCE athletes_id_seq;
            """

        regions_table_exists= session.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'regions'
                )
            """).fetchone()[0]
        
        create_regions_table_query = """
            CREATE TABLE regions (
                noc CHAR(3) PRIMARY KEY,
                region VARCHAR,
                notes VARCHAR
            );
        """

        athletes_summer_table_exists = session.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'athletes_summer'
            )
        """).fetchone()[0]

        create_athletes_summer_table_query = """
            CREATE TABLE athletes_summer (
                id INTEGER DEFAULT nextval('athletes_id_seq') PRIMARY KEY,
                name VARCHAR(255),
                sex CHAR(1),
                age FLOAT,
                team VARCHAR(255),
                noc CHAR(3) REFERENCES regions (noc) ON DELETE CASCADE ON UPDATE CASCADE,
                games VARCHAR(255),
                year INTEGER,
                season VARCHAR(255),
                city VARCHAR(255),
                sport VARCHAR(255),
                event VARCHAR(255),
                medal VARCHAR,
                CONSTRAINT check_medal CHECK (medal IN ('Gold', 'Silver', 'Bronze'))
            );
        """
        athletes_winter_table_exists = session.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'athletes_winter'
            )
        """).fetchone()[0]

        create_athletes_winter_table_query = """
            CREATE TABLE athletes_winter (
                id INTEGER DEFAULT nextval('athletes_id_seq') PRIMARY KEY,
                name VARCHAR(255),
                sex CHAR(1),
                age FLOAT,
                team VARCHAR(255),
                noc CHAR(3) REFERENCES regions (noc) ON DELETE CASCADE ON UPDATE CASCADE,
                games VARCHAR(255),
                year INTEGER,
                season VARCHAR(255),
                city VARCHAR(255),
                sport VARCHAR(255),
                event VARCHAR(255),
                medal VARCHAR,
                CONSTRAINT check_medal CHECK (medal IN ('Gold', 'Silver', 'Bronze'))
            );
        """

        # Copy data from CSV files
        copy_regions_query = """
            COPY regions(noc, region, notes)
            FROM '/var/lib/postgresql/csv_data/regions_clean.csv'
            DELIMITER ','
            CSV HEADER;
        """

        copy_athletes_summer_query = """
            COPY athletes_summer(name, sex, age, team, noc, games, year, season, city, sport, event, medal)
            FROM '/var/lib/postgresql/csv_data/Athletes_summer_games_clean.csv'
            DELIMITER ','
            CSV HEADER;
        """

        copy_athletes_winter_query = """
            COPY athletes_winter(name, sex, age, team, noc, games, year, season, city, sport, event, medal)
            FROM '/var/lib/postgresql/csv_data/Athletes_winter_games_clean.csv'
            DELIMITER ','
            CSV HEADER;
        """

    # Execute the queries
    # with Session(engine) as session:
        if not sequence_exists:
            session.execute(create_sequences_query)
        if not regions_table_exists:
            session.execute(create_regions_table_query)
            session.execute(copy_regions_query)
        if not athletes_summer_table_exists:
            session.execute(create_athletes_summer_table_query)
            session.execute(copy_athletes_summer_query)
        if not athletes_winter_table_exists:
            session.execute(create_athletes_winter_table_query)
            session.execute(copy_athletes_winter_query)
        session.commit()
    # Commit the changes
    # conn.commit()


    # Execute the copy queries
    # with Session(engine) as session:
    #     session.commit()

# Commit the changes

# Close the cursor and connection
# session.close()
# engine.close()
