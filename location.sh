#!/bin/bash

# Enable exit on error
set -e

# Function to send email notification
send_notification() {
    echo "A Python script has failed." | mail -s "HOW location job failure" cmedcoff@gmail.com
}

# Trap errors and call the notification function
#trap 'send_notification' ERR

cd /home/azureuser/how/location

# remove previous csv file
rm -f member_mapping.csv

# remove html cache from previous 'crawl'
rm -rf htmlindex && sync

# perform a new crawl
./env/bin/python3 crawl_with_playwright.py

# generate csv file from crawl
./env/bin/python3 parse_html_to_csv_for_db_import.py

# mail out the file as attachment
./env/bin/python3 mail.py

echo "All scripts executed successfully."

