# Snowflake Metadata API

A RESTful API service that provides endpoints for querying Snowflake metadata.

## Features

- List all databases
- List all schemas in a database
- List all tables in a schema
- Get detailed column information for tables
- Get table summaries with statistics

## Dependencies
- [fastapi](https://fastapi.tiangolo.com/): Framework for building REST APIs, runs on uvicorn
- [uvicorn](https://pypi.org/project/uvicorn/): ASGI web server
- [snowflake-connector-python](https://pypi.org/project/snowflake-connector-python/): For connecting to Snowflake
- [python-dotenv](https://pypi.org/project/python-dotenv/): For loading environment variables from a `.env` file
- [cachetools](https://pypi.org/project/cachetools/): For caching API responses etc.
- [pydantic](https://pydantic-docs.helpmanual.io/): For validating and parsing data

## Setup

1. Set up Pyenv if not already installed: https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv 

2. Switch to python version specified in `.python-version` using pyenv:
```bash
pyenv install
```

3. Install dependencies:
```bash
pyenv exec pip install -r requirements.txt
```

4. Create a `.env` file with your Snowflake credentials:
```
SNOWFLAKE_ACCOUNT_ID=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
```

5. Run the server:
```bash
pyenv exec uvicorn app.main:app --reload
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
- If the current query slowness is okay, then we can let snowflake take care of by spilling to disk. Otherwse we might have to create a ETL etc to build a separate just for distinct values.

The issue #2 however is not relevant to us as as we are only using COUNT that has max value of 10^38, which is a crazy number. And other methods like AVG/MIN/MAX will not overflow.

## Logs
Sat Feb 1
- 08:25 Reading through docs - ~10m
- 08:35 BREAK - ~30m
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
Mon Feb 3
- 08:00-08:30: fix docs ~30m

### Submittion QA
How long did you actually spend on this take-home?
- Took around 4 hrs to satisfy all requirements
- Took another 2 hrs to clean things up and document things

What was one thing that you thought went well in this exercise?
- Really enjoyed learning python and its ecosystem
- Setting up basic server with fast api and snowflake connector was super quick and easy
- Thinking through db OOM issues was fun

What is something that you’d want to improve if you had more time
- Look into if connection pool is relevant here, instead of opening a new connection to snowflake for each request
- Do the dependency injection of repo into cache functions and extract params as keys
- Batch same requests in into a single query
- Spend time on understanding how to optimize the summarization
    - Look into [Sampling](https://docs.snowflake.com/en/sql-reference/constructs/sample)
    - Look into [Cardinality Estimation](https://docs.snowflake.com/en/user-guide/querying-approximate-cardinality)
    - Look into [Other optimization techniques](https://select.dev/posts/snowflake-query-optimization)

Futher context need to productionize:
- Use case: Deep dive into who are users using it and for what purpose?
- Scalability: What does the flow if traffic looks like over a time period?
- Availability: Does this service needs to be available 24x7?
- Security: What are the boundaries of who can access this service?
