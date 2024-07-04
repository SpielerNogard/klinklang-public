import os
import re
import time
from typing import List

import requests
from imap_tools import A, MailBox
from pydantic import BaseModel

from klinklang.core.logger import Logger

SERVICE_NAME = "MailReader"
logger = Logger(SERVICE_NAME)


class MailBoxConfig(BaseModel):
    imap_server: str
    username: str
    password: str


class EmailReaderConfig(BaseModel):
    activated: bool = False
    mail_boxes: List[MailBoxConfig] = []


class EmailReader:
    def __init__(self, klinklang_server_url: str):
        self._server_url = klinklang_server_url

    def get_service_config(self) -> EmailReaderConfig:
        resp = requests.get(
            f"{self._server_url}/service/config", params={"service": SERVICE_NAME}
        )
        config = resp.json()["config"]
        if config:
            return EmailReaderConfig(**config)
        return EmailReaderConfig()

    def send_service_heartbeat(self):
        requests.post(
            f"{self._server_url}/service/heartbeat", params={"service": SERVICE_NAME}
        )

    def start(self):
        def run_service(config: EmailReaderConfig):
            if config.activated is True:
                logger.info(f"service {SERVICE_NAME} is activated")
                while True:
                    for mail_box in config.mail_boxes:
                        try:
                            logger.info(f"Checking mails {mail_box=}")
                            self.check_emails(mail_box)
                        except Exception as exc:
                            logger.error(f"Error while checking mails {exc=}")
                    self.send_service_heartbeat()
            else:
                time.sleep(60)
                logger.warning(
                    f"service {SERVICE_NAME} is not activated. Checking again in 60 seconds"
                )

        while True:
            config = self.get_service_config()
            run_service(config)

    def send_code_to_server(self, code: str, email: str):
        requests.post(f"{self._server_url}/code", data={"code": code, "email": email})

    def check_emails(self, mail_box: MailBoxConfig):
        with MailBox(mail_box.imap_server).login(
            mail_box.username, mail_box.password
        ) as mailbox:
            messages = [msg for msg in mailbox.fetch(A(seen=False), mark_seen=True)]

            for message in messages:
                logger.info("Received a new message")
                code = re.search(r"<h2>(\d{6})</h2>", message.html)
                if code:
                    code = code.group(1)
                    for to in message.to:
                        logger.info(f"Code found: {code} for {to=}")
                        self.send_code_to_server(code=code, email=to)
                        logger.info("Code send to server")
                if message.from_ == "no-reply@tmi.pokemon.com":
                    mailbox.delete(uid_list=[message.uid])
                    logger.info("Deleted message from Niantic")

                #  TODO we should probably delete the message from the bin


if __name__ == "__main__":
    host = os.environ["KLINKLANG_SERVER_URL"]
    reader = EmailReader(klinklang_server_url=host)
    reader.start()
