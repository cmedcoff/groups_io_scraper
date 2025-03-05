import logging
import traceback

from parse_common import write_csv_file, parse_user_profile_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

try:
    file_name = "member_mapping.csv"
    cols = [
        "Display Name",
        "State/Province or Country",
        "Zip/Postal Code",
        "Profile Link",
    ]
    write_csv_file(file_name, cols, parse_user_profile_data)

except Exception as ex:
    logger.error(f"An error occurred: {ex}")
    logger.error(traceback.format_exc())
