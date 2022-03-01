"""Utilitary package.
"""
import logging
import os
from datetime import datetime


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
