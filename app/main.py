from typing import List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException

from .lib import cache_factory, SnowflakeClient
from . import metadata

# Load .env environment variables
load_dotenv()


def get_metadata_repository():
    repo = metadata.Repository(client=SnowflakeClient())
    try:
        yield repo
    finally:
        repo.close()


def get_cache(ttlCache: cache_factory.TTLCache):
    def cache_gen():
        cache = cache_factory.APICache(cache=ttlCache)
        yield cache

    return cache_gen


# Create APIs
app = FastAPI(title="Snowflake Metadata API")


@app.get("/dbs", response_model=List[metadata.models.Database])
def list_dbs(
    repo: metadata.Repository = Depends(get_metadata_repository),
    cache: cache_factory.APICache = Depends(get_cache(cache_factory.dbs_cache)),
):
    """List all databases in the configured database."""

    def get_dbs():
        return repo.get_databases()

    return cache.getCacheOrRefresh(["dbs"], get_dbs)


@app.get("/dbs/{db_name}/schemas", response_model=List[metadata.models.Schema])
def list_schemas(
    db_name: str,
    repo: metadata.Repository = Depends(get_metadata_repository),
    cache: cache_factory.APICache = Depends(get_cache(cache_factory.schemas_cache)),
):
    """List all schemas in the specified database."""

    def get_schemas():
        try:
            return repo.get_schemas(db_name)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Database {db_name} not found")

    return cache.getCacheOrRefresh([db_name], get_schemas)


@app.get(
    "/dbs/{db_name}/schemas/{schema_name}/tables",
    response_model=List[metadata.models.Table],
)
def list_tables(
    db_name: str,
    schema_name: str,
    repo: metadata.Repository = Depends(get_metadata_repository),
    cache: cache_factory.APICache = Depends(get_cache(cache_factory.tables_cache)),
):
    """List all tables in the specified schema."""

    def get_tables():
        try:
            return repo.get_tables(db_name, schema_name)
        except Exception:
            raise HTTPException(
                status_code=404, detail=f"Schema {schema_name} not found"
            )

    return cache.getCacheOrRefresh([db_name, schema_name], get_tables)


@app.get(
    "/dbs/{db_name}/schemas/{schema_name}/tables/{table_name}/columns",
    response_model=List[metadata.models.Column],
)
def get_columns(
    db_name: str,
    schema_name: str,
    table_name: str,
    repo: metadata.Repository = Depends(get_metadata_repository),
    cache: cache_factory.APICache = Depends(get_cache(cache_factory.columns_cache)),
):
    """Get detailed information about all columns in the specified table."""

    def get_columns():
        try:
            return repo.get_columns(db_name, schema_name, table_name)
        except Exception:
            raise HTTPException(
                status_code=404, detail=f"Table {schema_name}.{table_name} not found"
            )

    return cache.getCacheOrRefresh([db_name, schema_name, table_name], get_columns)


@app.get(
    "/dbs/{db_name}/schemas/{schema_name}/tables/{table_name}/summary",
    response_model=metadata.models.TableSummary,
)
def get_table_summary(
    db_name: str,
    schema_name: str,
    table_name: str,
    repo: metadata.Repository = Depends(get_metadata_repository),
    cache: cache_factory.APICache = Depends(get_cache(cache_factory.summary_cache)),
):
    """Get summary statistics for all columns in the specified table."""

    def get_table_summary():
        try:
            return repo.get_table_summary(db_name, schema_name, table_name)
        except Exception:
            raise HTTPException(
                status_code=404, detail=f"Table {schema_name}.{table_name} not found"
            )

    return cache.getCacheOrRefresh(
        [db_name, schema_name, table_name], get_table_summary
    )
