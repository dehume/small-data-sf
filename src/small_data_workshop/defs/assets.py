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


@dg.asset
def github_archive_files(
    context: dg.AssetExecutionContext,
) -> str: ...


# @dg.asset()
# def github_archive_files(
#     context: dg.AssetExecutionContext,
# ) -> str: ...


# @dg.asset()
# def issues(
#     context: dg.AssetExecutionContext,
# ): ...


# @dg.asset_check()
# def github_events_check(): ...


# @dg.asset()
# def embedding_files(): ...


# @dg.asset()
# def embeddings(
#     context: dg.AssetExecutionContext,
# ): ...


# @dg.asset()
# def vss_index(
#     context: dg.AssetExecutionContext,
# ): ...


# class GithubIssue(dg.Config): ...


# @dg.asset()
# def similarity_search(
#     context: dg.AssetExecutionContext,
# ) -> dg.MaterializeResult: ...
