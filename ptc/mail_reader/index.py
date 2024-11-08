import re
import time
from itertools import cycle

from imap_tools import MailBox, A
from klinklang import logger
from klinklang.core.config import read_config
from klinklang.core.models.mail_reader_config import MailBox as MailConfig

config = read_config()
logger.info("Config loaded")
database_client = config.database.client()
logger.info("Connected to database")


def check_emails(config: MailConfig):
    # get subjects of unseen emails from INBOX folder
    with MailBox(config.imap_server).login(config.username, config.password) as mailbox:
        messages = [msg for msg in mailbox.fetch(A(seen=False), mark_seen=True)]

        for message in messages:
            logger.info("Received a new message")
            code = re.search(r"<h2>(\d{6})</h2>", message.html)
            if code:
                code = code.group(1)
                for to in message.to:
                    logger.info(f"Code found: {code} for {to=}")
                    database_client["codes"].insert_one({"code": code, "email": to})
                    logger.info(f"Code saved in database")
            if message.from_ == "no-reply@tmi.pokemon.com":
                mailbox.delete(uid_list=[message.uid])
                logger.info(f"Deleted message from Niantic")


if __name__ == "__main__":
    import os

    mail_reader_config = config.mailreader
    if mail_reader_config is None:
        logger.info("Mail reader config not found. MailReader disabled.")
        while True:
            time.sleep(6000000)

    sleep_time = int(os.environ.get("SLEEP_TIME", 1))
    domains = config.mailreader.mailbox
    servers = cycle(domains)
    while True:
        server = next(servers)
        logger.info(f"Checking mails {server=}")
        check_emails(server)

        time.sleep(sleep_time)
