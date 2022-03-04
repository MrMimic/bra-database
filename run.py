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

try:
    base_path = os.environ["BRA_LOG_FOLDER"]
except KeyError:
    base_path=os.path.join(os.sep, "logs")
logger = get_logger(base_path=base_path)


# Download the BRA files of the day
today = datetime.today().strftime("%Y%m%d")
try:
    pdf_path = os.environ["BRA_PDF_FOLDER"]
except KeyError:
    pdf_path = os.path.join(os.sep, "bra", today)
if not os.path.exists(pdf_path):
    os.makedirs(pdf_path)
downloader = BraDownloader(pdf_path=pdf_path, logger=logger)
downloader.get_json_timestamp_file()
downloader.get_pdf_files()

# Prepare the PDF parser and the DB credentials
credentials = DbCredentials()
parser = PdfParser(logger=logger)

for file in os.listdir(pdf_path):
    structured_data = parser.parse(os.path.join(pdf_path, file))
    with BraInserter(credentials=credentials, logger=logger) as inserter:
        inserter.insert(structured_data)
