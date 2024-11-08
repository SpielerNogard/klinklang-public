from typing import Optional

import yaml
from pydantic import BaseModel

from .models.account_export_config import AccountExportConfig
from .models.klinklang_database_config import DatabaseConfig
from .models.mail_reader_config import MailReaderConfig
from .models.mail_server_config import MailServerConfig


class Config(BaseModel):
    """
    Configuration for the klinklang service

    Parameters
    ----------
    database : DatabaseConfig
        The database configuration.
    mailserver : Optional[MailServerConfig]
        The mail server configuration.
    mailreader : Optional[MailReaderConfig]
        The mail reader configuration.
    domains : DomainConfig
        The domain configuration.
    export : Optional[AccountExportConfig]
        The account export configuration.

    """

    database: DatabaseConfig
    mailserver: Optional[MailServerConfig]
    mailreader: Optional[MailReaderConfig]
    export: Optional[AccountExportConfig]


def read_config(filename: str = "config.yml") -> Config:
    """
    Reads the configuration from a file

    Parameters
    ----------
    filename : str
        The filename of the configuration file.
        default: "config.yml"

    Returns
    -------
    Config
        The configuration object.
    """
    with open(filename, "r") as config_file:
        config = yaml.safe_load(config_file)
    return Config(**config)
