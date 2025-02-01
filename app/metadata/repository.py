from typing import List
import time

from . import models
from ..lib import SnowflakeClient


class Repository:
    def __init__(self, client: SnowflakeClient):
        self.conn = client.conn

    def get_databases(self) -> List[models.Database]:
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            return [models.Database(name=database[1]) for database in databases]

    def get_schemas(self, db_name: str) -> List[models.Schema]:
        with self.conn.cursor() as cursor:
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {db_name}")
            schemas = cursor.fetchall()
            return [models.Schema(name=schema[1]) for schema in schemas]

    def get_tables(self, db_name: str, schema: str) -> List[models.Table]:
        with self.conn.cursor() as cursor:
            cursor.execute(f"SHOW TABLES IN {db_name}.{schema}")
            tables = cursor.fetchall()
            return [models.Table(name=table[1]) for table in tables]

    def get_columns(self, db_name: str, schema: str, table: str) -> List[models.Column]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    COMMENT,
                    IS_NULLABLE
                FROM {db_name}.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """,
                (schema, table),
            )
            columns = cursor.fetchall()
            return [
                models.Column(
                    name=col[0], type=col[1], description=col[2] if col[2] else None
                )
                for col in columns
            ]

    def get_table_summary(
        self, db_name: str, schema: str, table: str
    ) -> models.TableSummary:
        columns = self.get_columns(db_name, schema, table)

        # Build an optimized query that gets all summary statistics in one go
        numeric_cols = []
        non_numeric_cols = []

        for col in columns:
            if col.type.upper() in ("NUMBER", "FLOAT", "INTEGER", "DECIMAL"):
                numeric_cols.append(col.name)
            else:
                non_numeric_cols.append(col.name)

        select_parts = ["COUNT(*) as row_count"]

        # Add numeric column summaries
        for col in numeric_cols:
            select_parts.extend(
                [
                    f"COUNT({col}) as {col}_non_null_count",
                    f"AVG({col}) as {col}_mean",
                    f"MIN({col}) as {col}_min",
                    f"MAX({col}) as {col}_max",
                ]
            )

        # Add non-numeric column summaries
        for col in non_numeric_cols:
            select_parts.extend(
                [
                    f"COUNT({col}) as {col}_non_null_count",
                    # f"COUNT(DISTINCT {col}) as {col}_unique_count",
                    f"APPROX_COUNT_DISTINCT({col}) as {col}_approx_unique_count",
                ]
            )

        query = f"""
            SELECT {", ".join(select_parts)}
            FROM {db_name}.{schema}.{table}
        """

        with self.conn.cursor() as cursor:
            start_time = time.time()
            cursor.execute(query)
            result = cursor.fetchone()
            query_time_ms = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Process results
            row_count = result[0]
            current_idx = 1

            column_summaries = {}

            # Process numeric columns (5 metrics each)
            for col in numeric_cols:
                column_summaries[col] = models.NumericSummary(
                    non_null_count=result[current_idx],
                    mean=result[current_idx + 1],
                    min=result[current_idx + 2],
                    max=result[current_idx + 3],
                )
                current_idx += 4

            # Process non-numeric columns (2 metrics each)
            for col in non_numeric_cols:
                column_summaries[col] = models.NonNumericSummary(
                    non_null_count=result[current_idx],
                    unique_count=result[current_idx + 1],
                )
                current_idx += 2

            return models.TableSummary(
                table_name=table,
                row_count=row_count,
                column_summaries=column_summaries,
                query_time_ms=query_time_ms,
            )

    def close(self):
        self.conn.close()
