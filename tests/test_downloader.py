"""Test covering the downloader class.
"""
import os
import shutil
import tempfile
import unittest

from bra_database.downloader import BraDownloader


class DownloaderTests(unittest.TestCase):
    """Test cases for the downloader class.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.downloader = BraDownloader(self.tmp)

    def tearDown(self) -> None:
        # Remove the temp folder
        shutil.rmtree(self.tmp)

    def test_download_json(self):
        """Test the JSON downloader class.
        """
        self.assertIsInstance(self.downloader, BraDownloader)
        self.downloader.get_json_timestamp_file(date="20220303")
        self.assertIsInstance(self.downloader.timestamps_bra, list)
        self.assertTrue(len(self.downloader.timestamps_bra) > 1)

    def test_download_pdf(self):
        """Test the PDF downloader class.
        """
        self.downloader.get_json_timestamp_file(date="20220303")
        self.downloader.timestamps_bra = self.downloader.timestamps_bra[0:1]
        self.downloader.get_pdf_file()
        self.assertTrue(len(os.listdir(self.tmp)) == 1)
