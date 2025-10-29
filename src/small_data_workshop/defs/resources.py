# flake8: noqa: F811, F401
from dagster_duckdb import DuckDBResource

import dagster as dg

database_resource_storage = DuckDBResource(database="workshop.duckdb")


@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "duckdb_storage": database_resource_storage,
        }
    )
