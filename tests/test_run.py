"""Test the global bra-db.
"""
import os
import unittest

from bra_database.parser import PdfParser
from bra_database.inserter import BraInserter


class ParserTests(unittest.TestCase):
    """Test cases for the parser module.
    """

    def setUp(self) -> None:
        self.parser = PdfParser()
        self.data = os.path.join(os.path.dirname(__file__), "data")

    def test_runtime(self) -> None:
        """Complete test used to developp the process.
        """
        for file in os.listdir("out"):
            structured_data = self.parser.parse(os.path.join("out", file))
            with BraInserter(user=os.environ["MYSQL_USR"],
                             password=os.environ["MYSQL_PWD"],
                             port=os.environ["MYSQL_PORT"]) as inserter:
                inserter.insert(structured_data)
                query = "SELECT massif FROM france;"
                data = inserter.exec_query(query)
            break
