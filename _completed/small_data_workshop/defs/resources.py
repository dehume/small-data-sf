from dagster_duckdb import DuckDBResource

import dagster as dg

database_resource_memory = DuckDBResource(database=":memory:")
database_resource_storage = DuckDBResource(database="workshop.duckdb")


@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "duckdb_memory": database_resource_memory,
            "duckdb_storage": database_resource_storage,
        }
    )
