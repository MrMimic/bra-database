"""Test covering the downloader class.
"""
import unittest

from bra_database.downloader import BraDownloader


class DownloaderTests(unittest.TestCase):
    """Test cases for the downloader class.
    """

    def setUp(self) -> None:
        self.downloader = BraDownloader()

    def test_downloader(self):
        """Test the downloader class.
        """
        self.assertIsInstance(self.downloader, BraDownloader)
        self.downloader.get_json_timestamp_file()
