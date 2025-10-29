import dagster as dg

from small_data_workshop.defs.assets import (
    github_archive_files,
    issues,
    embedding_files,
    embeddings,
    vss_index,
    similarity_search,
)


ingestion_job = dg.define_asset_job(
    name="ingestion_job",
    selection=[
        github_archive_files,
        issues,
        embedding_files,
        embeddings,
        vss_index,
    ],
)

similarity_search_job = dg.define_asset_job(
    name="similarity_search_job",
    selection=[similarity_search],
)
