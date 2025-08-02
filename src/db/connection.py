"""
Database connection module. Currently supports DuckDB.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from sqlalchemy import create_engine

import duckdb
import pandas as pd


# Abstract base class for DB connections
class DBConn(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute(self, query: str, params=None):
        pass


class DuckDBConn(DBConn):
    def __init__(self, database=":memory:", read_only=False):
        """
        params:
            database: Path to the DuckDB file or ':memory:'.
            read_only: Open DB in read-only mode if True.
        """
        self.database = database
        self._read_only = read_only
        self._conn = None
        self._engine = None

    def __enter__(self):
        self._conn = duckdb.connect(database=self.database, read_only=self._read_only)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
            self._conn = None
        if self._engine:
            self._engine.dispose()
            self._engine = None

    def connect(self):
        if not self._conn:
            self._conn = duckdb.connect(
                database=self.database, read_only=self._read_only
            )
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
        if self._engine:
            self._engine.dispose()
            self._engine = None

    def execute(
        self, query: str, params: dict | None = None, ddl: bool = False
    ) -> pd.DataFrame | None:
        params = {} if params is None else params

        if self._conn:
            result = self._conn.execute(query, params)
            return None if ddl else result.df()

        with duckdb.connect(
            database=self.database, read_only=self._read_only
        ) as temp_conn:
            result = temp_conn.execute(query, params)
            return None if ddl else result.df()

    def execute_file(
        self, filepath: str, params: dict | None = None, ddl: bool = False
    ) -> pd.DataFrame | None:
        sql = Path(filepath).read_text()
        return self.execute(sql, params=params, ddl=ddl)

    def sqlalchemy_engine(self):
        """
        Returns a SQLAlchemy engine using duckdb-engine.
        """
        if not self._engine:
            conn_str = f"duckdb:///{self.database}"
            self._engine = create_engine(conn_str)
        return self._engine


def create_db_connection(config: dict) -> DBConn:
    db_type = config.get("db_type", "").lower()
    if db_type == "duckdb":
        database = config.get("database", ":memory:")
        read_only = config.get("read_only", False)
        return DuckDBConn(database=database, read_only=read_only)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
