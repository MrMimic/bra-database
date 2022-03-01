"""Module used to parse PDF files.
"""
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import cv2
import pdfplumber
import pytesseract
from pytesseract.pytesseract import TesseractError

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
    risk_score: int = None
    """
    Main risk score of the BRA
    """
    risk_str: str = None
    """
    Risk as a non-structured sentence.
    """
    typical_situation: str = None
    """
    Situations avalancheuses typiques
    """


class PdfParser():
    """Parse a PDF file and extract structured information to be used in IA models later.
    """

    def __init__(self, logger: logging.Logger = None, image_output_path: str = None) -> None:
        """Initialise and set attributes.
        """
        self.logger = logger or get_logger()
        self.image_output_path = image_output_path if image_output_path else "IMG"
        # Utilities
        self.months = FrenchMonthsNumber()
        # Regexps
        self.r_massif = r"\s?MASSIF\s?:\s?(.*)\s?"
        self.r_date = r"rédigé le .*? ([0-9]{1,2}.*) à .*\."
        self.r_until = r"\s?[Jj]usqu'au .*? ([0-9]{1,2}.*[0-9]{2,4}).*\s?"
        self.r_departs_spontanes = r"\s?Départs spontanés\s?:\s?(.*?)\.?\s?Déclenchements skieurs"
        self.r_declanchement_skieurs = r"\s?Déclenchements skieurs\s?:\s?(.*?)\.?\s?Indices de risque"
        self.r_risk_str = r"Estimation des risques jusqu'au .*\n(.*)\.?\nDéparts spontanés"
        self.r_typical_situation = r"Situations avalancheuses typiques\s?:\s?(.*?)\.?\s?Départs spontanés"

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
            match = re.search(regexp, text).group(1).replace(".", "").lower()
        except AttributeError:
            match = None
        return match

    def _get_massif(self, text: str) -> str:
        """Get the massif if the BRA.
        """
        massif = self._get_from_regexp(text, self.r_massif)
        if massif:
            massif = massif.replace("/", "_")
        return massif

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

    def _get_risk_str(self, text: str) -> str:
        """Get the risk score of the BRA.
        """
        return self._get_from_regexp(text, self.r_risk_str)

    def _get_typical_situation(self, text: str) -> str:
        """Get the risk score of the BRA.
        """
        return self._get_from_regexp(text.replace("\n", ""), self.r_typical_situation)

    def _extract_and_save_image(self, page: pdfplumber.PDF, image: pdfplumber.PDF, image_path: str) -> None:
        """Extract and save an image from a PDF page.
        """
        page_height = page.height
        image_bbox = (image['x0'], page_height - image['y1'], image['x1'], page_height - image['y0'])
        cropped_page = page.crop(image_bbox)
        image_obj = cropped_page.to_image(resolution=400)
        image_obj.save(image_path)

    def _get_risk_int(self, image_path: str) -> int:
        """Analyse the image with OCR to extract the risk of avalanche.
        Because yeah, the main score of this data is only accessible through an image.
        """
        self.logger.info(f"Analysing image {image_path}")

        img = cv2.imread(image_path)
        # Crop the image to reduce the noise in OCR
        cropped_image = img[0:60, 0:60]
        # Apply OCR with different models properties
        chracters = []
        for oem in range(0, 4):
            for psm in range(0, 15):
                custom_oem_psm_config = f"--oem {oem} --psm {psm}"
                img_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
                try:
                    raw_detection = pytesseract.image_to_string(img_rgb, config=custom_oem_psm_config)
                    character = raw_detection.replace("\n", "").replace("\x0c", "").replace(" ",
                                                                                            "").encode("utf8").decode()
                    if character != "":
                        self.logger.debug(f"OEM: {oem}, PSM: {psm}, text: {character}")
                        chracters.append(character)
                except (TesseractError, FileNotFoundError):
                    continue
        # Get the maximum represented item (maximum vote from CV2 model)
        risk = max(chracters, key=chracters.count)
        try:
            risk = int(risk)
        except ValueError:
            self.logger.error(f"OCR retrived max item {risk} that is not an integer among {chracters}.")
            risk = None
        return risk

    def parse(self, file_path: str) -> None:
        """Parse a PDF file and extract informations based on regexps matching.
        """
        self.logger.info(f"Parsing file {file_path}")
        structured_data = StructuredData()
        with pdfplumber.open(file_path) as pdf:

            for index, page in enumerate(pdf.pages):
                # Extracting informations
                print(page.extract_text())
                structured_data = self._insert_info(structured_data, self._get_massif(page.extract_text()), "massif")
                structured_data = self._insert_info(structured_data, self._get_date(page.extract_text()), "date")
                structured_data = self._insert_info(structured_data, self._get_until(page.extract_text()), "until")
                structured_data = self._insert_info(structured_data, self._get_departs_spontanes(page.extract_text()),
                                                    "departs")
                structured_data = self._insert_info(structured_data,
                                                    self._get_declanchement_skieurs(page.extract_text()),
                                                    "declanchements")
                structured_data = self._insert_info(structured_data, self._get_risk_str(page.extract_text()),
                                                    "risk_str")
                structured_data = self._insert_info(structured_data, self._get_typical_situation(page.extract_text()),
                                                    "typical_situation")

                # Extract the avalanche risk score from the image that contains it in the first page
                if index == 0:
                    risk_image = [img for img in page.images if img["name"] == "Im10"]
                    if len(risk_image) != 1:
                        self.logger.error(f"No risk image found in BRA {file_path}")
                    else:
                        image = risk_image[0]
                        image_path = os.path.join(self.image_output_path, f"{structured_data.massif}_risks.jpg")
                        self.logger.info(f"Extracting risk image from page {index + 1} to {image_path}")
                        self._extract_and_save_image(page, image, image_path)
                        structured_data = self._insert_info(structured_data, self._get_risk_int(image_path),
                                                            "risk_score")

        return structured_data
