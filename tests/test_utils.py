"""Utils-related tests.
"""
import logging
import os
import shutil
import tempfile
import unittest
from datetime import datetime

from bra_database.utils import get_logger


class UtilsTests(unittest.TestCase):
    """Test cases for the utils module.
    """

    def setUp(self) -> None:
        # Create a temp folder
        self.tmp = tempfile.mkdtemp()

    def tearDown(self) -> None:
        # Remove the temp folder
        shutil.rmtree(self.tmp)

    def test_get_logger(self):
        """Test the logger module.
        """
        logger = get_logger(self.tmp)
        self.assertIsInstance(logger, logging.Logger)
        # Test log file writing
        logger.info("tests")
        today = datetime.today().strftime("%Y%m%d")
        self.assertIn(f"{today}_bra_database.log", os.listdir(self.tmp))
