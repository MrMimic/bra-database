"""Module handling downloading the different BRA PDF files.
"""
import logging
from datetime import datetime

import requests

from bra_database.utils import get_logger


class BraDownloader():
    """Download PDF files.
    """

    def __init__(self, logger: logging.Logger = None):
        """Initialize the class.
        """
        self.logger = logger or get_logger()

    @staticmethod
    def _create_file_path(date: str = None) -> str:
        """Concatenate the date of today with the expected JSON URL.

        returns:
            str: The expected file path.
        """
        if not date:
            date = datetime.today().strftime("%Y%m%d")
        file_path = f"https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/bra.{date}.json"
        return file_path

    def get_json_timestamp_file(self) -> None:
        """A JSON file contains the timestamps of the files to be downloaded.
        """
        json_file_path = self._create_file_path(date="20220228")
        self.logger.info(f"Downloading {json_file_path}")
        json_file = requests.get(json_file_path).json()
        print(json_file)
