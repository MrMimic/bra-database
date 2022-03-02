"""Insert structured data into a GCP MySQL database.
"""
from bra_database.parser import StructuredData
import pymysql
from typing import Any, get_type_hints
from bra_database.utils import get_logger

class BraInserter():
    """Insert structured data into an SQL database.
    """

    def __init__(self, password: str, host: str = "localhost", user: str = "root", port: int = 3306, database: str = "bra", table: str = "france") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.port = port
        self.logger = get_logger()
        # Check the base and create it if needed
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        cursor.execute(f"USE {self.database}")
        # Get the table description from the object structuring the data
        table_columns = ()
        self.table_columns = []
        for column, ctype in get_type_hints(StructuredData).items():
            self.table_columns.append(column)
            if ctype.__name__ == "str":
                table_columns += (f"{column} VARCHAR(1000)", )
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
        query = f"CREATE TABLE IF NOT EXISTS {self.database}.{self.table} (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(table_columns)})"
        cursor.execute(query)
        connection.commit()
        connection.close()

    def __enter__(self) -> None:
        """Get a connection.
        """
        self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.database, port=self.port)
        return self

    def __exit__(self, *exec_info) -> None:
        """Clear the connection
        """
        self.connection.commit()
        self.connection.close()

    def get_cursor(self) -> pymysql.cursors.Cursor:
        """Get a cursor.
        """
        return self.connection.cursor()

    def insert(self, structured_data: StructuredData) -> None:
        """Insert a structured data extracted from PDF BRA.
        """
        data = ()
        for columns in self.table_columns:
            data += (getattr(structured_data, columns), )
        query = f"INSERT INTO {self.database}.{self.table} ({', '.join(self.table_columns)}) VALUES ({', '.join(['%s' for _ in self.table_columns])})"
        self.connection.cursor().execute(query, data)

    def exec_query(self, query: str) -> Any:
        """Execute a query.
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        data = [row for row in cursor]
        return data
