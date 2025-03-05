import csv
import logging
import os
import re
import sys

from diskcache import Index
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

locations = {
    # United States
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "DC",
    # Canadian provinces
    "ON": "Ontario",
    "QC": "Quebec",
    "NS": "Nova Scotia",
    "NB": "New Brunswick",
    "MB": "Manitoba",
    "BC": "British Columbia",
    "SK": "Saskatchewan",
    "AB": "Alberta",
    # World Countries
    "Australia": "Australia",
    "Austria": "Austria",
    "Belgium": "Belgium",
    "Canada": "Canada",
    "Denmark": "Denmark",
    "England": "England",
    "France": "France",
    "Germany": "Germany",
    "Hong Kong": "Hong Kong",
    "India": "India",
    "Ireland": "Ireland",
    "Israel": "Israel",
    "New Zealand": "New Zealand",
    "Poland": "Poland",
    "Portugal": "Portugal",
    "Uganda": "Uganda",
    "UK": "UK",
    "Singapore": "Singapore",
}


def profile_url_and_page_from_cache():
    """generator to loop over html cache key/value pairs"""
    html_cache = Index(os.path.join(os.getcwd(), "htmlindex"))
    for profile_address in html_cache.keys():
        yield profile_address, html_cache[profile_address]


def location(display_name):
    geo = "Undetermined"
    match = re.search(
        r"\b("
        + "|".join(locations.keys())
        + "|"
        + "|".join(locations.values())
        + r")\b",
        display_name,
    )
    if match:
        geo = match.group()
        # If the match is a full state name, get the corresponding abbreviation
        if geo in locations.values():
            geo = list(locations.keys())[list(locations.values()).index(geo)]
    return geo


def parse_user_profile_data():
    """parse user profile data from cache and return a dictionary.
    The dictionary key is the user's profile address and the value is a tuple
    containing the user's display name and postal code. If the user's
    postal code is not found, the value is set to "99999".
    """
    for profile_address, profile_html in profile_url_and_page_from_cache():

        logger.debug(f"Processing profile: {profile_address}")
        if not profile_html:
            logger.error(f"Profile {profile_address} has no html")
            continue
            # sys.exit(1)

        soup = BeautifulSoup(profile_html, "html.parser")
        # find how user/profile's display name, skip on failure, no point in
        # trying to determine a user/profile's location if we can't determine
        # who the user is
        h3 = soup.find("h3")
        if not h3 or not h3.text:
            continue
        display_name = h3.text.split("Message")[0].strip()
        # find the postal code label and then it's parent p tag in order to
        # extract the postal code field/value so that this value can be written
        # to the CSV file
        postal_code = "99999"
        if l := soup.find("label", string=lambda x: x and x.strip() == "Postal Code"):
            if p := l.find_parent("p"):
                postal_code = p.get_text().split("Postal Code")[1].strip()
        yield display_name, location(display_name), postal_code, profile_address


def write_csv_file(file_name, column_headings, data):
    """write data to a CSV file"""
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_headings)
        for row in data():
            writer.writerow(row)
