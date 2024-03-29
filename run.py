"""Run the project, on a daily basis.
"""
from datetime import datetime
import os

from dotenv import load_dotenv

from bra_database.downloader import BraDownloader
from bra_database.inserter import BraInserter
from bra_database.parser import PdfParser
from bra_database.utils import DbCredentials, get_logger

# Load credentials if found locally
load_dotenv()


# Download the BRA files of the day
try:
    today = os.environ["BRA_DATE"]
except KeyError:
    today = datetime.today().strftime("%Y%m%d")

# Get a distinct logger each day
try:
    base_path = os.environ["BRA_LOG_FOLDER"]
except KeyError:
    base_path = os.path.join(os.sep, "logs")
logger = get_logger(base_path=base_path, file_name=f"{today}_bra_database.log")

# Download PDF files
try:
    pdf_path = os.environ["BRA_PDF_FOLDER"]
except KeyError:
    pdf_path = os.path.join(os.sep, "bra", today)
if not os.path.exists(pdf_path):
    os.makedirs(pdf_path)
downloader = BraDownloader(pdf_path=pdf_path, logger=logger)
downloader.get_json_timestamp_file(date=today)
downloader.get_pdf_files()

# Prepare the PDF parser and the DB credentials
credentials = DbCredentials(logger=logger)
try:
    image_output_path = os.environ["BRA_IMG_FOLDER"]
except KeyError:
    image_output_path = os.path.join(os.sep, "img")
parser = PdfParser(logger=logger, image_output_path=image_output_path)

for index, file in enumerate(os.listdir(pdf_path)):
    logger.info(f"Parsing file {index + 1}/{len(os.listdir(pdf_path))}")
    structured_data = parser.parse(os.path.join(pdf_path, file))
    with BraInserter(credentials=credentials, logger=logger) as inserter:
        inserter.insert(structured_data)
