"""
This script executes external SQL files to create schemas and load CSV data.

Usage:
    python create_schema_and_load_data.py 
"""

import argparse
import logging
import os
import yaml
from db.connection import create_db_connection

# --- Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(SCRIPT_DIR, "..", "data_model", "sql")
CSV_DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data/raw_csv")
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
DEFAULT_SQL_FILES = [
    "model/staging_schema.sql",
    "model/analysis_schema.sql",
    "load/load_staging_data.sql",
    "load/load_analysis_data.sql"
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)


def _arg_parse():
    parser = argparse.ArgumentParser(description="Build DB schema and load data from SQL files.")
    parser.add_argument(
        "--config-path",
        type=str,
        default=f"{DATA_DIR}/duckdb_config.yaml",
        help="Path to DB YAML config file."
    )
    parser.add_argument(
        "--sql-dir",
        type=str,
        default=SQL_DIR,
        help="Root directory containing SQL files."
    )
    parser.add_argument(
        "--sql-paths",
        nargs="+",
        default=DEFAULT_SQL_FILES,
        help="List of SQL files or directories (relative to --sql-dir) to run."
    )
    parser.add_argument(
        "--csv-path-dir",
        type=str,
        default=CSV_DATA_DIR,
        help="Directory containing CSV files to substitute into load_staging_data.sql files."
    )
    return parser.parse_args()


def _get_sql_files(base_dir, paths):
    sql_files = []
    for path in paths:
        abs_path = os.path.join(base_dir, path)
        if os.path.isdir(abs_path):
            dir_files = [
                os.path.join(abs_path, f)
                for f in sorted(os.listdir(abs_path))
                if f.endswith(".sql") and os.path.isfile(os.path.join(abs_path, f))
            ]
            sql_files.extend(dir_files)
        elif os.path.isfile(abs_path) and abs_path.endswith(".sql"):
            sql_files.append(abs_path)
        else:
            _logger.warning(f"Skipping invalid or non-SQL path: {abs_path}")
    return sql_files


def _execute_sql_files(conn, sql_files, csv_files):
    csv_index = 0
    for sql_file in sql_files:
        filename = os.path.basename(sql_file)

        with open(sql_file, "r") as f:
            sql_template = f.read()
        if "load_staging_data.sql" in filename:
           for csv_file in csv_files:
                if csv_file.endswith(".csv"):
                    csv_index += 1
                    _logger.info(f"Injecting CSV file {csv_index}: {csv_file}")
                    sql = sql_template.replace("@csv_path@", csv_file)
                    _logger.info(f"Inserting CSV {csv_file} into staging.raw_table")
                    conn.execute(sql, ddl=True)
        else:
            sql = sql_template
            _logger.info(f"Executing SQL: {sql_file}")
            conn.execute(sql, ddl=True)

if __name__ == "__main__":
    args = _arg_parse()

    with open(args.config_path) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)
    csv_files = [
        os.path.join(args.csv_path_dir, f)
        for f in os.listdir(args.csv_path_dir)
        if f.endswith('.csv')
    ]    
    sql_files = _get_sql_files(args.sql_dir, args.sql_paths)
    _execute_sql_files(conn, sql_files, csv_files)
