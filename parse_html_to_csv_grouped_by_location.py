import itertools
import logging
import traceback

from parse_common import write_csv_file, parse_user_profile_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def profiles_sorted_and_grouped_by_location():
    # tuple of (display_name, state_province_or_country, postal_code, url) so
    # sort/group by state_province_or_country, e.g. index 1
    s = sorted(parse_user_profile_data(), key=lambda x: x[1])
    i = itertools.groupby(s, lambda x: x[1])
    for k, v in i:
        for v2 in v:
            yield v2


try:
    file_name = "grouped_member_mapping.csv"
    cols = [
        "Display Name",
        "State/Province or Country",
        "Zip/Postal Code",
        "Profile Link",
    ]
    write_csv_file(file_name, cols, profiles_sorted_and_grouped_by_location)

except Exception as ex:
    logger.error(f"An error occurred: {ex}")
    logger.error(traceback.format_exc())
