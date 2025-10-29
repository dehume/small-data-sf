# flake8: noqa: F811, F401
import os
import dagster as dg
from datetime import datetime
from sentence_transformers import SentenceTransformer
from dagster_duckdb import DuckDBResource
import pandas as pd

from small_data_workshop.constants import (
    ISSUES_TABLE_NAME,
    EMBEDDINGS_TABLE_NAME,
    INDEX_NAME,
    EMBEDDING_DIMENSION,
    MODEL_NAME,
)

daily_partitions_def = dg.HourlyPartitionsDefinition(
    start_date="2025-10-01-00:00+0000",
    end_date="2025-10-02-00:00+0000",
)


# Intermediate step
@dg.asset
def github_archive_files(
    context: dg.AssetExecutionContext,
) -> str:
    return "https://data.gharchive.org/2025-10-01-0.json.gz"


# Intermediate step
@dg.asset
def github_archive_files(
    context: dg.AssetExecutionContext,
    duckdb_storage: DuckDBResource,
) -> str:
    with duckdb_storage.get_connection() as conn:
        file_name = "https://data.gharchive.org/2025-10-01-0.json.gz"
        conn.execute(
            f"""
            copy (
                select * from read_json_auto('{file_name}', 
                    ignore_errors=true,
                    union_by_name=true,
                    sample_size=-1
                )
                where type = 'IssuesEvent'
                and payload.action = 'opened'
            ) to 'data/raw/{file_name}.parquet' (format parquet)
            """
        )
    context.log.info(f"Downloaded - {file_name}")


@dg.asset(
    partitions_def=daily_partitions_def,
)
def github_archive_files(
    context: dg.AssetExecutionContext,
    duckdb_storage: DuckDBResource,
) -> str:
    partition_date = datetime.strptime(context.partition_key, "%Y-%m-%d-%H:%M")
    url_partition = partition_date.strftime("%Y-%m-%d") + f"-{partition_date.hour}"

    if os.path.exists(f"data/raw/{url_partition}.parquet"):
        context.log.info(f"File already exists - {url_partition}")
    else:
        with duckdb_storage.get_connection() as conn:
            gharchive_url = f"https://data.gharchive.org/{url_partition}.json.gz"
            conn.execute(
                f"""
                copy (
                    select * from read_json_auto('{gharchive_url}', 
                        ignore_errors=true,
                        union_by_name=true,
                        sample_size=-1
                    )
                    where type = 'IssuesEvent'
                    and payload.action = 'opened'
                ) to 'data/raw/{url_partition}.parquet' (format parquet)
                """
            )
        context.log.info(f"Downloaded - {url_partition}")

    return url_partition


@dg.asset(
    partitions_def=daily_partitions_def,
    kinds={"duckdb"},
    group_name="duckdb_memory",
)
def github_archive_files(
    context: dg.AssetExecutionContext,
    duckdb_memory: DuckDBResource,
) -> str:
    partition_date = datetime.strptime(context.partition_key, "%Y-%m-%d-%H:%M")
    url_partition = partition_date.strftime("%Y-%m-%d") + f"-{partition_date.hour}"

    if os.path.exists(f"data/raw/{url_partition}.parquet"):
        context.log.info(f"File already exists - {url_partition}")
    else:
        with duckdb_memory.get_connection() as conn:
            gharchive_url = f"https://data.gharchive.org/{url_partition}.json.gz"
            conn.execute(
                f"""
                copy (
                    select * from read_json_auto('{gharchive_url}', 
                        ignore_errors=true,
                        union_by_name=true,
                        sample_size=-1
                    )
                    where type = 'IssuesEvent'
                    and payload.action = 'opened'
                ) to 'data/raw/{url_partition}.parquet' (format parquet)
                """
            )
        context.log.info(f"Downloaded - {url_partition}")

    return url_partition


@dg.asset(
    kinds={"duckdb"},
    deps=[github_archive_files],
    group_name="duckdb_storage",
    backfill_policy=dg.BackfillPolicy.single_run(),
)
def issues(
    context: dg.AssetExecutionContext,
    duckdb_storage: DuckDBResource,
):
    with duckdb_storage.get_connection() as conn:
        conn.execute(
            f"""
                create or replace table {ISSUES_TABLE_NAME} as
                select 
                    id,
                    org.login as org,
                    payload.issue.html_url as url,
                    payload.issue.user.login as author,
                    payload.issue.created_at as created_at,
                    payload.issue.title as title,
                    payload.issue.body as body
                from 'data/raw/*.parquet'
            """
        )


@dg.asset_check(
    asset=issues,
)
def github_events_check(
    duckdb_storage: DuckDBResource,
):
    with duckdb_storage.get_connection() as conn:
        events = conn.execute(
            f"""select count(*) from {ISSUES_TABLE_NAME}"""
        ).fetchall()
    return dg.AssetCheckResult(passed=len(events) > 0)


@dg.asset(
    kinds={"duckdb", "huggingface"},
    deps=[github_archive_files],
    group_name="duckdb_memory",
    partitions_def=daily_partitions_def,
)
def embedding_files(
    context: dg.AssetExecutionContext,
    duckdb_memory: DuckDBResource,
    github_archive_files: str,
):
    if os.path.exists(f"data/embeddings/{github_archive_files}.parquet"):
        context.log.info(f"File already exists - {github_archive_files}.parquet")
    else:
        model = SentenceTransformer(MODEL_NAME, cache_folder="models")
        context.log.info("Loaded model")

        with duckdb_memory.get_connection() as conn:
            df = conn.execute(f"""
                select 
                    id,
                    'Title: ' || payload.issue.title || ' Body: ' || coalesce(payload.issue.body, '') as combined_text
                from 'data/raw/{github_archive_files}.parquet'
            """).df()

            embeddings_list = model.encode(
                df["combined_text"].tolist(), show_progress_bar=True
            )

            df["embedding"] = [embedding.tolist() for embedding in embeddings_list]
            context.log.info(
                f"Generated embeddings with dimension: {len(embeddings_list[0])}"
            )

            conn.execute(f"""
                copy (
                    select 
                        id,
                        embedding::FLOAT[{EMBEDDING_DIMENSION}] as embedding
                    from df
                ) to 'data/embeddings/{github_archive_files}.parquet' (format parquet)
            """)


@dg.asset(
    kinds={"duckdb"},
    deps=[embedding_files],
    group_name="duckdb_storage",
    backfill_policy=dg.BackfillPolicy.single_run(),
)
def embeddings(
    context: dg.AssetExecutionContext,
    duckdb_storage: DuckDBResource,
):
    with duckdb_storage.get_connection() as conn:
        conn.execute(
            f"""
                create or replace table {EMBEDDINGS_TABLE_NAME} as
                select 
                    id,
                    embedding::FLOAT[{EMBEDDING_DIMENSION}] as embedding
                from 'data/embeddings/*.parquet'
            """
        )


@dg.asset(
    kinds={"duckdb"},
    deps=[embeddings],
    group_name="duckdb_storage",
)
def vss_index(
    context: dg.AssetExecutionContext,
    duckdb_storage: DuckDBResource,
):
    with duckdb_storage.get_connection() as conn:
        # Install and load the VSS extension
        conn.execute("INSTALL vss")
        conn.execute("LOAD vss")

        # Enable experimental persistence for the HNSW index
        conn.execute("SET hnsw_enable_experimental_persistence = true")

        # Create HNSW index on the embedding column
        conn.execute(f"""drop index if exists {INDEX_NAME}""")

        context.log.info("Creating HNSW index")
        conn.execute(f"""
            create index if not exists {INDEX_NAME} 
                on {EMBEDDINGS_TABLE_NAME} 
                using hnsw (embedding) 
                with (m = 16, ef_construction = 200)
        """)


class GithubIssue(dg.Config):
    id: str
    similarity_score: float = 0.75
    num_results: int = 5


@dg.asset(
    kinds={"duckdb"},
    deps=[embeddings, vss_index, issues],
    group_name="similarity_search",
)
def similarity_search(
    context: dg.AssetExecutionContext,
    config: GithubIssue,
    duckdb_storage: DuckDBResource,
) -> dg.MaterializeResult:
    with duckdb_storage.get_connection() as conn:
        # Issue data
        issue_data = conn.execute(f"""
            select
                title,
                author,
                url,
            from {ISSUES_TABLE_NAME}
            where id = {config.id}
        """).fetchone()

        # Similar issues
        similar_issues = conn.execute(f"""
            select
                ie.id,
                i.url,
                array_cosine_similarity(ie.embedding, q.query_vec) as similarity
            from
                {EMBEDDINGS_TABLE_NAME} as ie,
                (
                    select
                        embedding as query_vec
                    from {EMBEDDINGS_TABLE_NAME}
                    where id = {config.id}
                ) as q
            join {ISSUES_TABLE_NAME} as i
                on ie.id = i.id
            where ie.id != {config.id}
            and array_cosine_similarity(ie.embedding, q.query_vec) > {config.similarity_score}
            order by array_cosine_similarity(ie.embedding, q.query_vec) desc
            limit {config.num_results};
        """).fetchall()

        return dg.MaterializeResult(
            metadata={
                "id": config.id,
                "title": issue_data[0],
                "author": issue_data[1],
                "url": dg.MetadataValue.url(issue_data[2]),
                "similar_issues": similar_issues,
            }
        )
