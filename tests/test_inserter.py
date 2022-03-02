"""Inserter module
"""
import unittest

from bra_database.inserter import BraInserter


class InserterTests(unittest.TestCase):
    """Test inserter
    """

    def setUp(self) -> None:
        """Initialize tests
        """
        self.connection = BraInserter(user="root", password="9326995", port=3309)


    def test_connection(self) -> None:
        """Test the connection to the database.
        """
        self.assertIsInstance(self.connection, BraInserter)
        with self.connection as conn:
            self.assertTrue("exec_query" in dir(conn))
