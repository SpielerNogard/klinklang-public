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

        # Save the original body for processing
        body_original = data.decode("utf-8", errors="replace")  # Replace invalid bytes

        # Create a lowercase version for keyword matching
        body_lower = body_original.lower()

        # Extract 6-digit code if present
        match = re.search(r"<h2>(\d{6})</h2>", body_original)
        code = match.group(1) if match else None

        # Detect specific email types
        is_registered   = "registration complete" in body_lower
        is_password     = "password reset" in body_lower
        is_verification = "verify email" in body_lower

        # Gather all recipient email addresses
        parsed_mime_message = email.message_from_bytes(data)
        to = parsed_mime_message.get("To")
        emails = [to, *rcpttos]

        # Process and log based on email type
        for mail in emails:
            if mail:  # Ensure the email address is valid
                if is_password:
                    logger.info(f"email={mail} type=password code={code}")
                elif code:  # Default to activation when code present
                    logger.info(f"email={mail} type=activation code={code}")
                    database_client["codes"].insert_one({"code": code, "email": mail})
                    logger.info(f"email={mail} type=code_saved")
                elif is_registered:
                    logger.info(f"email={mail} type=registered")
                else:
                    logger.info(f"email={mail} type=other No code found")

        # Show whole email if verifying a relay destination address
        # Process after main paths. Raw email chars may be problematic
        if is_verification:
            try:
                logger.info(f"type=verification Full email body:\n{body_original}")
            except Exception as e:
                logger.error(f"type=verification_failed Could not log email body. Error: {e}")


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
