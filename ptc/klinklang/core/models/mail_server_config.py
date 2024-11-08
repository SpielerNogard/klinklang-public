from pydantic import BaseModel


class MailServerConfig(BaseModel):
    """
    Configuration for the mail server.

    Parameters
    ----------
    port : int
        The port inside the container, where the mail server should be openened.
        default: 25
    host : str
        The IP where the mail server should be opened.
        default: 0.0.0.0
    """

    port: int = 25
    host: str = "0.0.0.0"
