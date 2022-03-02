"""Utilitary package.
"""
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List
from dataclasses import dataclass

@dataclass
class FrenchMonthsNumber:
    """French months numbers.
    """
    janvier: int = 1
    février: int = 2
    mars: int = 3
    avril: int = 4
    mai: int = 5
    juin: int = 6
    juillet: int = 7
    août: int = 8
    septembre: int = 9
    octobre: int = 10
    novembre: int = 11
    décembre: int = 12

class StabiliteManteauKeys():
    """
    Under the "Stabilité du manteau neigeux" text bloc, the keys of the text are not consistents.
    To structure them, for now, this class only store words that should be retireved.
    """
    def __init__(self):
        self.situation_avalancheuse_typique: List[str] = ["typique", "avalancheuse"]
        self.departs_spontanes: List[str] = ["spontané"]
        self.declanchements_provoques: List[str] = ["skieurs", "déclanchement"]

    def retrieve_best_match(self, text: str) -> str:
        """Retrieve the best match of a text in the list of keys.
        """
        for key, words in self.__dict__.items():
            for word in words:
                if word in text:
                    return key
        return None

def get_logger(base_path: str = None) -> logging.Logger:
    """Define and returns a logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Format
    formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    # File handler
    if not os.path.exists("logs"):
        os.makedirs("logs")
    execution_date = datetime.today().strftime("%Y%m%d")
    log_path = os.path.join("logs", f"{execution_date}_bra_database.log") if not base_path else os.path.join(
        base_path, f"{execution_date}_bra_database.log")
    if os.path.exists(log_path):
        os.remove(log_path)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
