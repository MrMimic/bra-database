"""Module used to parse PDF files.
"""
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pdfplumber

from bra_database.utils import FrenchMonthsNumber, get_logger


@dataclass
class StructuredData:
    """Data class to store the parsed data.
    """
    massif: str = None
    date: str = None
    until: str = None
    departs: str = None
    declanchements: str = None


class PdfParser():
    """Parse a PDF file and extract structured information to be used in IA models later.
    """

    def __init__(self, logger: logging.Logger = None) -> None:
        """Initialise and set attributes.
        """
        self.logger = logger or get_logger()
        # Utilities
        self.months = FrenchMonthsNumber()
        # Regexps
        self.r_massif = r"\s?MASSIF\s?:\s?(.*)\s?"
        self.r_date = r"rédigé le .*? ([0-9]{1,2}.*) à .*\."
        self.r_until = r"\s?[Jj]usqu'au .*? ([0-9]{1,2}.*[0-9]{2,4}).*\s?"
        self.r_departs_spontanes = r"\s?Départs spontanés\s?:\s?(.*?)\.?\s?Déclenchements skieurs"
        self.r_declanchement_skieurs = r"\s?Déclenchements skieurs\s?:\s?(.*?)\.?\s?Indices de risque"

    @staticmethod
    def _insert_info(structured_data: StructuredData, data: Any, key: str) -> StructuredData:
        """Insert an attribute info a structured data object.
        """
        if data is not None:
            setattr(structured_data, key, data)
        return structured_data

    @staticmethod
    def _get_from_regexp(text: str, regexp: str) -> str:
        """Extract the first group match from a regexp.
        """
        try:
            match = re.search(regexp, text).group(1)
        except AttributeError:
            match = None
        return match

    def _get_massif(self, text: str) -> str:
        """Get the massif if the BRA.
        """
        return self._get_from_regexp(text, self.r_massif)

    def _get_date(self, text: str) -> str:
        """Get the date of the BRA.
        """
        date = self._get_from_regexp(text, self.r_date)
        if date:
            for month in dir(self.months):
                if month in date:
                    date = date.replace(month, str(self.months.__getattribute__(month)))
                    date = datetime.strptime(date, "%d %m %Y")
                    break
        return date

    def _get_until(self, text: str) -> str:
        """Get the date of validity of the BRA.
        """
        until = self._get_from_regexp(text, self.r_until)
        if until:
            for month in dir(self.months):
                if month in until:
                    until = until.replace(month, str(self.months.__getattribute__(month)))
                    until = datetime.strptime(until, "%d %m %Y")
                    break
        return until

    def _get_departs_spontanes(self, text: str) -> str:
        """Get the risk of autonomous avalanche starts.
        """
        return self._get_from_regexp(text.replace("\n", " "), self.r_departs_spontanes)

    def _get_declanchement_skieurs(self, text: str) -> str:
        """Get how an avalanche can be triggered by a skier.
        """
        return self._get_from_regexp(text.replace("\n", " "), self.r_declanchement_skieurs)

    def parse(self, file_path: str) -> None:
        """Parse a PDF file and extract informations based on regexps matching.
        """
        self.logger.debug(f"Parsing {file_path}")
        structured_data = StructuredData()
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                structured_data = self._insert_info(structured_data, self._get_massif(page.extract_text()), "massif")
                structured_data = self._insert_info(structured_data, self._get_date(page.extract_text()), "date")
                structured_data = self._insert_info(structured_data, self._get_until(page.extract_text()), "until")
                structured_data = self._insert_info(structured_data, self._get_departs_spontanes(page.extract_text()),
                                                    "departs")
                structured_data = self._insert_info(structured_data,
                                                    self._get_declanchement_skieurs(page.extract_text()),
                                                    "declanchements")
        return structured_data
