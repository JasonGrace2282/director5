from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Literal, override

import mysql.connector
import psycopg
from psycopg import sql as psql

from ..docker.schema import DatabaseInfo


class DatabaseError(Exception):
    def __init__(self, ty: Literal["postgres", "mysql"], ex: Exception):
        super().__init__()
        self.ty = ty
        self.ex = ex


class DatabaseHandler(ABC):
    def __init__(self, db_info: DatabaseInfo):
        self.db_info = db_info

    @abstractmethod
    def create_database(self) -> None:
        """Create a database using the provided database information."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    def delete_database(self) -> None:
        """Delete a database using the provided database information."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    def run_query(self, db: str, query: str) -> str:
        """Run a query on the database using the provided database information."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class MySqlHandler(DatabaseHandler):
    @contextmanager
    def open_cursor(self, db: str, *, admin: bool = False):
        kwargs = {}
        hostname = self.db_info.host.admin_hostname

        if hostname.startswith("/"):
            kwargs["unix_socket"] = hostname
            hostname = "localhost"

        if admin:
            port = self.db_info.host.admin_port
            user = self.db_info.host.admin_username
            password = self.db_info.host.admin_password
        else:
            port = self.db_info.db_port
            user = self.db_info.username
            password = self.db_info.password

        conn = mysql.connector.connect(
            host=hostname,
            port=port,
            user=user,
            passwd=password,
            database=db,
            **kwargs,
        )
        try:
            yield conn.cursor()

            conn.commit()
        finally:
            conn.close()


class PostgresHandler(DatabaseHandler):
    @contextmanager
    def open_cursor(self, db: str, *, admin: bool = False):
        hostname = self.db_info.host.admin_hostname
        if admin:
            port = self.db_info.host.admin_port
            user = self.db_info.host.admin_username
            password = self.db_info.host.admin_password
        else:
            port = self.db_info.db_port
            user = self.db_info.username
            password = self.db_info.password

        with psycopg.connect(
            host=hostname,
            port=port,
            user=user,
            password=password,
            dbname=db,
        ) as conn:
            with conn.cursor() as cursor:
                yield cursor

    @override
    def create_database(self) -> None:
        with self.open_cursor("postgres", admin=True) as cursor:
            # Check if the user exists
            _ = cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_user WHERE usename = %s",
                (self.db_info.username,),
            )
            query = (
                "CREATE USER {} WITH PASSWORD %s"
                if cursor.rowcount == 0
                else "ALTER USER {} WITH PASSWORD %s"
            )
            _ = cursor.execute(
                psql.SQL(query).format(psql.Identifier(self.db_info.username)),
                (self.db_info.password,),
            )
            _ = cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_info.db_name,),
            )

            # Create database and set privileges for the user
            if cursor.rowcount == 0:
                _ = cursor.execute(
                    psql.SQL("CREATE DATABASE {} WITH OWNER = %s ENCODING 'UTF8'").format(
                        psql.Identifier(self.db_info.db_name),
                    ),
                    (self.db_info.host.admin_username,),
                )

            _ = cursor.execute(
                psql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    psql.Identifier(self.db_info.db_name),
                    psql.Identifier(self.db_info.username),
                )
            )

            _ = cursor.execute(
                psql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                    psql.Identifier(self.db_info.username),
                )
            )

    @override
    def delete_database(self) -> None:
        with self.open_cursor("postgres", admin=True) as cursor:
            _ = cursor.execute(
                psql.SQL("DROP DATABASE IF EXISTS {}").format(psql.Identifier(self.db_info.db_name))
            )

            _ = cursor.execute(
                psql.SQL("REVOKE ALL ON SCHEMA public FROM {}").format(
                    psql.Identifier(self.db_info.username)
                )
            )
            _ = cursor.execute(
                psql.SQL("DROP USER IF EXISTS {}").format(psql.Identifier(self.db_info.username))
            )

    @override
    def run_query(self, db: str, query: str) -> str:
        with self.open_cursor(db) as cursor:
            try:
                _ = cursor.execute(query)
            except psycopg.DatabaseError as e:
                raise DatabaseError("postgres", e) from e
            result = (
                "\t".join([desc[0] for desc in cursor.description]) if cursor.description else ""
            )
            for row in cursor:
                result += f"\n{'\t'.join(str(x) for x in row)}"
            return result
