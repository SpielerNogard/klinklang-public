from typing import List

from pydantic import BaseModel


class MailBox(BaseModel):
    """
    Configuration for a mail box, which should be read

    Parameters
    ----------
    username : str
        The username of the mail box.
    password : str
        The password of the mail box.
    imap_server : str
        The server under which the mail box is hosted.
    delete_after_read : bool
        If the mail should be deleted after reading it.
        default: True
    """

    username: str
    password: str
    imap_server: str
    delete_after_read: bool = True


class MailReaderConfig(BaseModel):
    """
    Configuration for the mail reader.

    Parameters
    ----------
    mailbox : List[MailBox]
        The mail boxes which should be read.
    """

    mailbox: List[MailBox]
