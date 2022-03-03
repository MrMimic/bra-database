"""Test the global bra-db.
"""
import os
import unittest

from bra_database.inserter import BraInserter
from bra_database.parser import PdfParser
from bra_database.utils import DbCredentials, get_logger
from dotenv import load_dotenv


class ParserTests(unittest.TestCase):
    """Test cases for the parser module.
    """

    def setUp(self) -> None:
        self.parser = PdfParser()
        self.data = os.path.join(os.path.dirname(__file__), "data")

    @unittest.skip("Meant to be run locally.")
    def RUN(self) -> None:
        """Complete test used to developp the process.
        """
        # Source .env file
        load_dotenv()
        logger = get_logger()
        parser = PdfParser(logger=logger)
        credentials = DbCredentials()
        for file in os.listdir("out"):
            structured_data = parser.parse(os.path.join("out", file))
            with BraInserter(credentials=credentials, logger=logger) as inserter:
                inserter.insert(structured_data)
                query = "SELECT * FROM france;"
                data = inserter.exec_query(query, output=True)
                print(data)
            break
