# Athlete API

The Athlete API is a web service built primarily using FastAPI and PostgreSQL with SQLModel/SQLAlchemy. Its goal is to provide information about athletes participating in the Olympic Games. Users can query the API to retrieve the number of medals an athlete has won and obtain general data about the athlete. Additionally, users can search for athletes based on criteria such as country, sport, and period.

The API leverages data, which includes two CSV files describing athletes who have participated in the Summer and Winter Olympic Games in the past years, as well as a CSV file that provides information about the National Olympic Committees (NOCs) and their respective regions.

The API is completely dockerized in two containers - one for the web and one for the db. Packages are managed using Poetry.

This README provides instructions on setting up and running the Athlete API project. It includes details on dependencies, environment setup, and running the application.

Detailed API documentation available at [Redoc](http://localhost:8000/redoc).

Interactive Demo at [Swagger](http://localhost:8000/docs).

## Features

- Retrieve the number of medals won by an athlete, their represented country, sport and years of participation. Further data on query request.
- Get stats of a country - total entries, unique participants, medal count, participation years - filtered by sport or time period.
- Or get stats of an NOC.
- CRUD on athlete data, NOC data

## Prerequisites

Before running the Athlete API, ensure you have the following prerequisites:

1. [Docker](https://www.docker.com/) installed on your system - Docker Daemon has to be running.
2. (1) is the only real requirement :) (2) Your favourite IDE/text editor to manipulate config values if needed.

## Installation and Setup

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/your-username/athlete-api.git
   ```

2. Navigate to the main project directory:
   ```
   cd athlete-api
   ```
   
3. Build the Docker image:
   ```
   docker compose build
   ```

## Running the Application

1. Start the Docker container:
   ```
   docker compose up -d
   ```
   -d flag to run in detached mode

2. The API will be accessible at http://localhost:8000
3. Stop the Docker container:
   ```
   docker compose down
   ```

4. (Optional) Access the postgresql instance:
   ```
   docker exec -it athlete-api-db-1 bash
   psql -h localhost -U {username(postgres)}
   ```
## API Documentation

The API documentation is automatically generated and available at http://localhost:8000/docs or http://localhost:8000/redoc when the application is running. It provides detailed information about the available endpoints, request/response formats, and example requests.

## Running Tests

To run the tests, run the docker web component and pytest.
```
docker compose up -d
docker exec -it athlete-api-web-1 bash
poetry run pytest
```

This command will run the test cases defined in the `tests` directory to ensure the functionality of the API.
More tests are under development

## Additional Notes

- The provided CSV files (`athletes_summer.csv`, `athletes_winter.csv`, `noc_regions.csv`) should be placed in the data directory.
- They have been stripped of the first column since it was not a unique primary key
- They will be autoloaded by a custom dataloader into the container on the first run and then stored in persistent storage of the container.
- Feel free to modify and extend the project to suit your specific needs.

For any issues or questions, please raise an Issue or contact [kevin.george@tum.de](mailto:kevin.george@tum.de).

---
