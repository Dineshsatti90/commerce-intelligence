"""Read-only analytical demo from the exact aggregate extracts committed to Git."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
TABLES = {"mart_monthly", "mart_retention", "mart_delivery", "mart_fulfillment", "mart_categories"}


def load_table(name: str) -> pd.DataFrame:
    if name not in TABLES:
        raise ValueError(f"Unknown aggregate table: {name}")
    frame = pd.read_csv(ROOT / "reports" / f"{name}.csv")
    for column in ("month", "cohort"):
        if column in frame:
            frame[column] = pd.to_datetime(frame[column])
    return frame


def query_records(query_id: str) -> list[dict]:
    """Run the same reviewed catalog against SQL views of committed CSVs."""
    import duckdb
    from copilot import CATALOG

    if query_id not in CATALOG:
        raise ValueError("Unknown query ID")
    if query_id == "overview":
        import json

        metrics = json.loads((ROOT / "reports/metrics.json").read_text())
        return [{k: metrics[k] for k in ("orders", "delivered_orders", "delivered_gmv_brl")}]
    with duckdb.connect(":memory:") as database:
        for table in TABLES:
            filename = (ROOT / "reports" / f"{table}.csv").as_posix().replace("'", "''")
            database.execute(f"CREATE VIEW {table} AS SELECT * FROM read_csv('{filename}', header=true)")
        cursor = database.execute(CATALOG[query_id]["sql"])
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
