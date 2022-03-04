"""Module handling downloading the different BRA PDF files.
"""
import logging
import os
import shutil
from datetime import datetime

import requests
from retry import retry

from bra_database.utils import get_logger


class BraDownloader():
    """Download PDF files.
    """

    def __init__(self, pdf_path: str, logger: logging.Logger = None):
        """Initialize the class.
        """
        self.logger = logger or get_logger()
        self.pdf_path = pdf_path
        self.file_name = []

        if not os.path.exists(self.pdf_path):
            os.makedirs(self.pdf_path)
        self.logger.info(f"Downloading data in folder: {self.pdf_path}")

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

    def get_json_timestamp_file(self, date: str = None) -> None:
        """A JSON file contains the timestamps of the files to be downloaded.
        """
        json_file_path = self._create_file_path(date=date)
        self.logger.info(f"Downloading JSON file listing BRA: {json_file_path}")
        self.timestamps_bra = requests.get(json_file_path).json()
        self.logger.info(f"{len(self.timestamps_bra)} BRA file to be downloaded.")

    @retry(tries=2, delay=10)
    def _download_file(self, file_name: str) -> None:
        """Download a BRA file.
        """
        file_path = os.path.join(self.pdf_path, file_name)
        if not os.path.isfile(file_path):
            bra_url = f"https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.{file_name}"
            self.logger.debug(f"Téléchargement de {bra_url}")
            response = requests.get(bra_url, stream=True)
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

    def get_pdf_files(self) -> None:
        """Download a PDF file.
        """
        for bra in self.timestamps_bra:
            for time in bra['heures']:
                file_name = f"{bra['massif']}.{time}.pdf"
                self.file_name.append(file_name)
                if file_name not in os.listdir(self.pdf_path):
                    self._download_file(file_name=file_name)
