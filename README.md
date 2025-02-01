# Snowflake Metadata API

A RESTful API service that provides endpoints for querying Snowflake metadata.

## Features

- List all databases
- List all schemas in a database
- List all tables in a schema
- Get detailed column information for tables
- Get table summaries with statistics

## Dependencies
- [fastapi](https://fastapi.tiangolo.com/): For building REST APIs
- [uvicorn](https://uvicorn.readthedocs.io/): Dev tooling for hot reloads
- [snowflake-connector-python](https://pypi.org/project/snowflake-connector-python/): For connecting to Snowflake
- [python-dotenv](https://pypi.org/project/python-dotenv/): For loading environment variables from a `.env` file
- [cachetools](https://pypi.org/project/cachetools/): For caching API responses
- [pydantic](https://pydantic-docs.helpmanual.io/): For validating and parsing data

## Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Create a `.env` file with your Snowflake credentials:
```
SNOWFLAKE_ACCOUNT_ID=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

Open API docs available at: http://127.0.0.1:8000/docs

Sample requests:
```bash
curl http://127.0.0.1:8000/dbs
curl http://127.0.0.1:8000/dbs/LONG_TAIL_COMPANIONS/schemas
curl http://127.0.0.1:8000/dbs/LONG_TAIL_COMPANIONS/schemas/ANALYTICS/tables
curl http://127.0.0.1:8000/dbs/LONG_TAIL_COMPANIONS/schemas/ANALYTICS/tables/DOG_BREED_CHARACTERISTICS/columns
curl http://127.0.0.1:8000/dbs/LONG_TAIL_COMPANIONS/schemas/ANALYTICS/tables/DOG_BREED_CHARACTERISTICS/summary
```

# Development notes

## Requirements

Build a python web server that exposes RESTful endpoints for querying snowflake metadata

### Functional

Needs following APIs
1. List all Schemas in a Database.
2. List all Tables in a Schema.
3. List each Column in a Table, including its name, type, and description.
4. Get a summary of a table, which returns summary statistics for each column.For numeric columns, it should include the non-null count, mean, min, and max of the column.For all other columns, it should include the non-null count and unique count. Try to use as few SQL queries as possible.

### Non-functional

- 2QPS
- Underlying data does not change very often.
- For the table summaries, it may be the case that some tables you need to query are extremely large and cannot be loading into memory fully.

## Assumptions

- Auth is not needed, will be hidden in a private net
- It is okay for the table summary statistics to deviate a bit

## Notes

Queries that can potentially be OOM in 2 ways:
1. The dataset aggregated into memory needs to hols too many rows
    - Do nothing as snowflake will Spill to Disk if Necessary
    - Query in batches
    - Optimize the query somehow - depends on the context
    - Offload the query to a ETL to avoid overloading db frequently
2. The an aggregated numeric value exceeds max integer/decimal value
    - This could happen when we are using SUM

For handling issue #1:
- One optimization we can do assuming approxmate statistics works is to use APPROX_COUNT_DISTINCT instead of COUNT(DISTINCT).
- If the current query slowness is okay, then we can let snowflake take care of by spilling to disk. Otherwse we might have to figure batching ideally within the query itself.

The issue #2 however is not relevant to us as as we are only using COUNT that has max value of 10^38, which is a crazy number. And other methods like AVG/MIN/MAX will not overflow.

## Logs
Sat Feb 1
- 8:25 Reading through docs - ~10m
- 8:35 BREAK - ~30m
- 09:30 Building a basic functional server - ~2h
    - Go through snowflake.connector
    - Go through fast api docs
    - Look for useful libs
    - Update local libs + download pyenv
    - Build a basic functional server
- 11:40 Satisfying non-functional requirements - ~2h
    - Setup code formatter + clean ups
    - Look at caching tools
    - Look at db OOM edge cases + optimized queries a bit
    - Take notes on potential ways to circumvent query slowness
- 13:40 Making codebase beautiful - ~1h
    - Played around with folder and import structure
- 14:40 Adding/updating notes/logs - ~30m
    - Update Log/Notes + Add everything to readme
- 15:15: Finish
