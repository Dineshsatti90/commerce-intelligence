"""Download the complete Olist release, ingest raw CSVs and build dbt marts."""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
import duckdb

ROOT = Path(__file__).resolve().parent
SOURCE = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce?datasetVersionNumber=2"
FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "categories": "product_category_name_translation.csv",
}


def download() -> None:
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = raw / "olist-v2.zip"
    if not archive.exists():
        tmp = archive.with_suffix(".part")
        request = urllib.request.Request(
            SOURCE, headers={"User-Agent": "AnalystPortfolio research contact portfolio@example.com"}
        )
        with urllib.request.urlopen(request, timeout=120) as r, tmp.open("wb") as f:
            shutil.copyfileobj(r, f)
        if not zipfile.is_zipfile(tmp):
            raise ValueError("Source did not return a ZIP; no placeholder data accepted")
        tmp.replace(archive)
    with zipfile.ZipFile(archive) as z:
        for filename in FILES.values():
            # Copy only expected flat CSV names, never arbitrary archive paths.
            with z.open(filename) as src, (raw / filename).open("wb") as dst:
                shutil.copyfileobj(src, dst)
    manifest = {
        "source": SOURCE,
        "publisher": "Olist via Kaggle",
        "dataset_version": 2,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "files": {},
    }
    for name, filename in FILES.items():
        p = raw / filename
        manifest["files"][name] = {
            "filename": filename,
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/source_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Downloaded and verified full Olist ZIP", flush=True)


def ingest() -> None:
    (ROOT / "warehouse").mkdir(exist_ok=True)
    db = duckdb.connect(str(ROOT / "warehouse/commerce.duckdb"))
    db.execute("create schema if not exists raw")
    counts = {}
    for name, filename in FILES.items():
        path = (ROOT / "data/raw" / filename).as_posix().replace("'", "''")
        # Explicit date columns belong in staging; preserve source strings on ingest.
        db.execute(
            f"create or replace table raw.{name} as select * from read_csv('{path}',header=true,all_varchar=true)"
        )
        counts[name] = db.execute(f"select count(*) from raw.{name}").fetchone()[0]
    db.close()
    (ROOT / "reports/row_counts.json").write_text(json.dumps(counts, indent=2))
    print(json.dumps(counts, indent=2), flush=True)
    if counts["orders"] < 99000 or counts["geolocation"] < 1000000:
        raise ValueError("Unexpected truncated release; refusing toy/subsample data")


def build() -> None:
    env = os.environ.copy()
    env["COMMERCE_DB"] = (ROOT / "warehouse/commerce.duckdb").as_posix()
    executable = shutil.which("dbt")
    if not executable:
        raise RuntimeError("Install requirements and activate the project virtual environment")
    subprocess.run(
        [executable, "build", "--project-dir", str(ROOT / "dbt"), "--profiles-dir", str(ROOT / "dbt")],
        env=env,
        check=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["download", "ingest", "build", "all"])
    args = p.parse_args()
    for cmd, fn in [("download", download), ("ingest", ingest), ("build", build)]:
        if args.command in (cmd, "all"):
            fn()
