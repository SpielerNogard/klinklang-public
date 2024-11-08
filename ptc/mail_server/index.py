import asyncore
import email
import re
import smtpd
import time

from klinklang import logger
from klinklang.core.config import read_config

config = read_config()
logger.info("Config loaded")
database_client = config.database.client()
logger.info("Connected to database")


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(
        self, peer, mailfrom, rcpttos, data, mail_options=None, rcpt_options=None
    ):
        logger.info("Received a new message")
        parsed_mime_message = email.message_from_bytes(data)
        # get 6 digit code from data (search for 6 digit ints which are surrounded in \n)
        code = re.search(r"<h2>(\d{6})</h2>", data.decode("utf-8"))
        if code:
            code = code.group(1)

            to = parsed_mime_message.get("To")
            emails = [to, *rcpttos]
            for mail in emails:
                logger.info(f"Code found: {code} for {email=}")
                database_client["codes"].insert_one({"code": code, "email": mail})
                logger.info(f"Code saved in database")
        else:
            logger.info(f"No code was found")


if __name__ == "__main__":
    mail_server_config = config.mailserver
    if mail_server_config is None:
        logger.info("Mail server config not found. MailServer disabled.")
        while True:
            time.sleep(6000000)
    server = CustomSMTPServer((mail_server_config.host, mail_server_config.port), None)
    logger.info(
        f"Server running on {mail_server_config.host}:{mail_server_config.port}"
    )
    asyncore.loop()
