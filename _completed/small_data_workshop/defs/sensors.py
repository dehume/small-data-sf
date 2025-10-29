import dagster as dg
from dagster_duckdb import DuckDBResource

from small_data_workshop.constants import ISSUES_TABLE_NAME, ORG_NAME


@dg.sensor(
    job_name="similarity_search_job",
    minimum_interval_seconds=60,
)
def new_issues_sensor(
    context: dg.SensorEvaluationContext,
    duckdb_storage: DuckDBResource,
):
    last_issue_id = context.cursor if context.cursor else "0"

    try:
        with duckdb_storage.get_connection() as conn:
            new_issues = conn.execute(f"""
                select id
                from {ISSUES_TABLE_NAME}
                where org = '{ORG_NAME}'
                and id > '{last_issue_id}'
            """).fetchall()

            if len(new_issues) > 0:
                context.log.info(f"Found {len(new_issues)} new issues")
            else:
                context.log.info("No new issues found")

        for issue in new_issues:
            issue_id = issue[0]

            # Update cursor to the highest issue ID
            if int(issue_id) > int(last_issue_id):
                last_issue_id = issue_id

            context.update_cursor(str(last_issue_id))

            yield dg.RunRequest(
                run_key=str(issue_id),
                run_config={
                    "ops": {
                        "similarity_search": {
                            "config": {
                                "id": issue_id,
                                "similarity_score": 0.1,
                                "num_results": 3,
                            }
                        }
                    }
                },
            )

    except Exception as e:
        return dg.SkipReason(f"Sensor failed with error: {str(e)}")
