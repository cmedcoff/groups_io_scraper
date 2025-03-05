from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
import os
import smtplib
import sys

from dotenv import load_dotenv

# set the current working directory for the purposes of the log file, the
# attachment, etch
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('mail.log'))

# TODO - rotating log? auto delete after 30 days?

def send_email():

    fromaddr = os.environ["MAIL_ADMIN"]
    toaddr = os.environ["MAIL_RECIPIENTS"]

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr.split(",")) # handle single or multiple sep by comma
    msg['Subject'] = "HOW groups.io location crawler results"

    body = "This is an automated message. \r\nPlease find attached the results of the HOW groups.io location crawler."
    msg.attach(MIMEText(body, 'plain'))

    filename = "member_mapping.csv"
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    with smtplib.SMTP(os.environ["MAIL_SERVER"], os.environ["MAIL_PORT"]) as server:
        server.starttls()
        server.login(fromaddr, os.environ["MAIL_PASSWORD"]) 
        text = msg.as_string()
        # apparently the 2nd param needs to be a list
        server.sendmail(fromaddr, toaddr.split(","), text)
        server.quit()

try:
    load_dotenv()
    send_email()
    sys.exit(0)
except Exception as e:
    logger.error(f"Error sending email: {e}")
    logger.exception(e)
    sys.exit(1)


