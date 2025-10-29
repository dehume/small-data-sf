# flake8: noqa: F811, F401
import dagster as dg
from dagster_duckdb import DuckDBResource

from small_data_workshop.constants import ISSUES_TABLE_NAME, ORG_NAME


# @dg.sensor(
#     job_name="similarity_search_job",
#     minimum_interval_seconds=60,
# )
# def new_issues_sensor(
#     context: dg.SensorEvaluationContext,
#     duckdb_storage: DuckDBResource,
# ):
#     ...
