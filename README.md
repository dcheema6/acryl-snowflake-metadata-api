# Snowflake Metadata API

A RESTful API service that provides endpoints for querying Snowflake metadata.

## Features

- List all databases
- List all schemas in a database
- List all tables in a schema
- Get detailed column information for tables
- Get table summaries with statistics

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
