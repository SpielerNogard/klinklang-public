from typing import Literal

from pydantic import BaseModel


class AccountExportConfig(BaseModel):
    """
    Configuration for exporting accounts to an external database.

    Parameters
    ----------
    enabled : bool
        Whether the account export is enabled.
        default: False
    rate : int
        The rate in seconds at which accounts are exported.
        default: 3600
    destination : Literal["DRAGONITE", "RDM"]
        The destination table of the accounts, either DRAGONITE or RDM.
    discord : bool
        Whether to send messages to Discord with stats.
        default: False
    webhook : str
        The webhook URL to send messages to Discord.
    host : str
        The IP of the database where the accounts should be imported to.
    password : str
        The password of the database, where the accounts should be imported to.
    username : str
        The username of the database, where the accounts should be imported to.
    db_name : str
        The name of the database, where the accounts should be imported to.
    table_name : str
        The table name to be used, where the accounts should be imported to.
    port : int
        The port where the database for importing is running.
        default: 3306
    """
    rate: int = 3600
    destination: Literal["DRAGONITE", "RDM"]
    discord: bool = False
    webhook: str = None
    host: str
    password: str
    username: str
    db_name: str
    table_name: str
    port: int = 3306
