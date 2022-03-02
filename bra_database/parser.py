"""Module used to parse PDF files.
"""
import json
import logging
import os
import re
from curses.ascii import isdigit
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

import cv2
import pdfplumber
import pytesseract
from pytesseract.pytesseract import TesseractError

from bra_database.utils import (FrenchMonthsNumber, StabiliteManteauKeys, get_logger)


@dataclass
class StructuredData:
    """Data class to store the parsed data.
    """
    original_link: str = None
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
    stabilite_manteau_bloc: str = None
    """
    The JSON bloc containing the 3 following keys.
    """
    situation_avalancheuse_typique: str = None
    """
    Situations avalancheuses typiques
    """
    departs_spontanes: str = None
    """
    Avalanches spontanées
    """
    declanchements_provoques: str = None
    """
    Déclenchements skieurs
    """
    qualite_neige: str = None
    """
    Quallité de la neige
    """

    def __repr__(self) -> None:
        return "- " + "\n- ".join([f"{key}: {value}" for key, value in self.__dict__.items()]) + "\n"


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
        self.r_stabilite_manteau = r"Stabilité du manteau neigeux(.*?)Neige fraîche à 1800 m"
        self.r_qualite_neige = r"Qualité de la neige(.*?)Tendance ultérieure des risques"

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

    def _get_stabilite_manteau(self, text: str) -> str:
        """This bloc of text is less structured than others.
        """
        # We keep track of the \n
        text_bloc = self._get_from_regexp(text.replace("\n", "::"), self.r_stabilite_manteau)
        if text_bloc:
            # Find the text keys
            r_keys = re.compile(r"\:\:([^:]*?) \: ")
            keys = re.findall(r_keys, text_bloc)
            # The text of each key is retrieved behing this one and the next
            texts = {}
            for index, key in enumerate(keys):
                try:
                    regexp = re.compile(f"{key}(.*?){keys[index + 1]}")
                except IndexError:
                    regexp = re.compile(f"{key}(.*?)$")
                text = " ".join(re.search(regexp, text_bloc).group(1).replace(":", " ").split())
                texts[key] = text
            return json.dumps(texts, ensure_ascii=False)
        return None

    @staticmethod
    def _insert_stabilite_manteau(structured_data: StructuredData, data: Dict[str, str]) -> str:
        """Insert stabilite manteau in a structured data object.
        """
        key_words_relations = StabiliteManteauKeys()
        # The keys of this text are not consdistent, they must be mapped.
        for key, value in data.items():
            best_match = key_words_relations.retrieve_best_match(key)
            if best_match:
                setattr(structured_data, best_match, value)
        return structured_data

    def _get_qualite_neige(self, text: str) -> str:
        """Get the risk of autonomous avalanche starts.
        """
        return self._get_from_regexp(text.replace("\n", " "), self.r_qualite_neige)

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
                    if character != "" and isdigit(character):
                        self.logger.debug(f"OEM: {oem}, PSM: {psm}, text: {character}")
                        # If the character is a number, add it to the list
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
        structured_data = StructuredData(
            original_link=
            f"https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.{file_path.split('/')[-1]}")
        with pdfplumber.open(file_path) as pdf:
            for index, page in enumerate(pdf.pages):
                # Extracting informations
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
                structured_data = self._insert_info(structured_data, self._get_qualite_neige(page.extract_text()),
                                                    "qualite_neige")
                structured_data = self._insert_info(structured_data, self._get_stabilite_manteau(page.extract_text()),
                                                    "stabilite_manteau_bloc")
                # Now this JSON should be parsed to get the 3 resulting keys
                structured_data = self._insert_stabilite_manteau(structured_data,
                                                                 json.loads(structured_data.stabilite_manteau_bloc))
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
