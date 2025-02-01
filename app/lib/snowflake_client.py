import os

import snowflake.connector


class SnowflakeClient:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT_ID"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        )
