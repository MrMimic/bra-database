"""Test the parser module.
"""
import os
import unittest
from datetime import datetime

from bra_database.parser import PdfParser


class ParserTests(unittest.TestCase):
    """Test cases for the parser module.
    """

    def setUp(self) -> None:
        self.parser = PdfParser()
        self.data = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self) -> None:
        pass

    def test_parse_pdf(self):
        """Test the PDF parser on an uploaded BRA.
        """
        structured_data = self.parser.parse(os.path.join(self.data, "BEAUFORTAIN.20220228150738.pdf"))
        self.assertEqual(structured_data.massif, "BEAUFORTAIN")
        self.assertEqual(structured_data.date, datetime(2022, 2, 28, 0, 0))
        self.assertEqual(structured_data.until, datetime(2022, 3, 1, 0, 0))
        self.assertEqual(structured_data.departs, "rares coulée")
        self.assertEqual(structured_data.declanchements, "quelques plaques en ubacs d'altitudes moyennes")
