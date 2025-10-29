import dagster as dg
from dagster_duckdb import DuckDBResource

import small_data_workshop.defs

from small_data_workshop.defs.assets import (
    github_archive_files,
    issues,
    embedding_files,
    embeddings,
    vss_index,
    similarity_search,
)

database_resource_memory = DuckDBResource(database=":memory:")
database_resource_storage = DuckDBResource(database="workshop.duckdb")


def test_ingestion_run():
    result = dg.materialize(
        assets=[
            github_archive_files,
            issues,
            embedding_files,
            embeddings,
            vss_index,
            similarity_search,
        ],
        partition_key="2025-10-01-12:00",
        resources={
            "duckdb_memory": database_resource_memory,
            "duckdb_storage": database_resource_storage,
        },
        run_config={
            "ops": {
                "similarity_search": {
                    "config": {
                        "id": 12345,
                        "similarity_score": 0.75,
                        "num_results": 5,
                    }
                }
            }
        },
    )
    assert result.success


def test_defs():
    assert dg.components.load_defs(small_data_workshop.defs)
