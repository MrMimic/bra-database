"""Insert structured data into a GCP MySQL database.
"""
import logging
from typing import Any, get_type_hints

import pymysql
from pymysql.err import IntegrityError

from bra_database.parser import StructuredData
from bra_database.utils import DbCredentials, get_logger


class BraInserter():
    """Insert structured data into an SQL database.
    """

    def __init__(self, credentials: DbCredentials, logger: logging.Logger = None) -> None:
        self.credentials = credentials
        # Logger
        self.logger = logger or get_logger()
        # Connection
        connection = pymysql.connect(host=self.credentials.host,
                                     user=self.credentials.user,
                                     password=self.credentials.password,
                                     port=self.credentials.port)
        # Database
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.credentials.database}")
            connection.commit()
        connection.select_db(self.credentials.database)
        # Table
        self.large_columns = [
            "stabilite_manteau_bloc", "declanchements_provoques", "situation_avalancheuse_typique", "departs_spontanes",
            "qualite_neige", ""
        ]
        query = self._get_create_query_bra_table()
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()
        connection.close()
        # Inserted files
        self.inserted_files = self.list_inserted_files_recently()

    def _get_create_query_bra_table(self) -> str:
        """Use the type hints from the StructuredData object to create a table.
        """
        table_columns = ()
        self.table_columns = []
        for column, ctype in get_type_hints(StructuredData).items():
            self.table_columns.append(column)
            if ctype.__name__ == "str":
                if column in self.large_columns:
                    varchar_size = 1500
                else:
                    varchar_size = 150
                table_columns += (f"{column} VARCHAR({varchar_size})", )
            elif ctype.__name__ == "int":
                table_columns += (f"{column} SMALLINT", )
            elif ctype.__name__ == "float":
                table_columns += (f"{column} FLOAT", )
            elif ctype.__name__ == "bool":
                table_columns += (f"{column} BOOLEAN", )
            elif ctype.__name__ == "datetime":
                table_columns += (f"{column} DATETIME", )
            else:
                self.logger.error(f"Unsupported type {ctype.__name__} from {column}")
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.credentials.database}.{self.credentials.table} \
            (id INT PRIMARY KEY AUTO_INCREMENT, {', '.join(table_columns)}, \
            CONSTRAINT unique_bra_each_day UNIQUE(original_link, massif, date)) \
            DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        return query

    def __enter__(self) -> None:
        """Get a connection.
        """
        self.connection = pymysql.connect(host=self.credentials.host,
                                          user=self.credentials.user,
                                          password=self.credentials.password,
                                          port=self.credentials.port,
                                          db=self.credentials.database)
        return self

    def __exit__(self, *exec_info) -> None:
        """Clear the connection
        """
        self.connection.commit()
        self.connection.close()

    def list_inserted_files_recently(self, days: int = 7) -> None:
        """List the original PDF file from the database that have been inserted less than a week ago.
        """
        query = f"""
            SELECT DISTINCT original_link 
            FROM {self.credentials.database}.{self.credentials.table}
            WHERE date > DATE_SUB(NOW(), INTERVAL {days} DAY)
        """
        return [file["original_link"] for file in self.exec_query(query, output=True)]

    def get_cursor(self) -> pymysql.cursors.DictCursor:
        """Get a cursor.
        """
        return self.connection.cursor(pymysql.cursors.DictCursor)

    def insert(self, structured_data: StructuredData) -> None:
        """Insert a structured data extracted from PDF BRA.
        """
        if structured_data.original_link not in self.inserted_files:
            data = ()
            for columns in self.table_columns:
                data += (getattr(structured_data, columns), )
            query = f"""
                INSERT INTO {self.credentials.database}.{self.credentials.table} \
                ({', '.join(self.table_columns)}) VALUES \
                ({', '.join(['%s' for _ in self.table_columns])})
            """
            self.exec_query(query, data)
        else:
            self.logger.info(f"Tried to insert already treated file {structured_data.original_link}")

    def exec_query(self, query: str, data: Any = None, output: bool = False) -> Any:
        """Execute a query.
        """
        self.logger.info(f"Executing {query.split()[0]} query on {self.credentials.database}.{self.credentials.table}")
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                if data:
                    cursor.execute(query, data)
                else:
                    cursor.execute(query)
            except IntegrityError as error:
                self.logger.error(str(error))
                return None
            self.connection.commit()
            if output:
                return cursor.fetchall()
            return None
