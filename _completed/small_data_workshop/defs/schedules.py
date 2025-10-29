import dagster as dg

from small_data_workshop.defs.jobs import ingestion_job

asset_partitioned_schedule = dg.build_schedule_from_partitioned_job(
    ingestion_job,
)
