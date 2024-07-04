from typing import Literal

from klinklang.core.database import db
from klinklang.core.models.proxies import Proxy
from klinklang.core.models.codes import Codes
from klinklang.core.models.logs import Logs
from klinklang.core.models.server_config import ServerConfig
from klinklang.core.models.worker import Worker

from peewee import MySQLDatabase
from klinklang.core.logger import Logger
from typing import List

logger = Logger("Database")
DB_VERSIONS = [1]

TABLES = [ServerConfig, Worker, Logs, Codes, Logs, Proxy]


class KlinklangDatabase:
    def __init__(self, db_type: Literal["mariadb", "mysql"], **kwargs):
        if db_type in ["mariadb", "mysql"]:
            db.initialize(MySQLDatabase(**kwargs))

        db.connect()
        # db.drop_tables(TABLES)
        db.create_tables(TABLES)

        current_db_version = self.get_db_version()
        if current_db_version is None:
            self.create_db_version()
        elif current_db_version == max(DB_VERSIONS):
            logger.info(f"Database is up to date at version {current_db_version}")
        else:
            self.update_db_version(current_db_version, max(DB_VERSIONS))

    def get_db_version(self):
        """
        Method to query the current database version.

        Returns
        -------
        int, optional
            The current database version.
        """
        try:
            try:
                return int(ServerConfig.get(ServerConfig.name == "db_version").value)
            except ValueError:
                return None
        except ServerConfig.DoesNotExist:
            return None

    def get_server_config(self, config_name: str) -> ServerConfig:
        return ServerConfig.get(ServerConfig.name == config_name)

    def create_db_version(self):
        """
        Method to create the database version, if no db version was found already.
        This will insert the highest version number from DB_VERSIONS into the database.
        """
        logger.info(f"No db version found using version {max(DB_VERSIONS)}")
        ServerConfig.create(name="db_version", value=max(DB_VERSIONS))

    def update_db_version(self, current_version: int, new_version: int):
        """
        Method to update the database version.
        This will also handle the migration of the database between versions.

        Parameters
        ----------
        current_version : int
            The current database version.
        new_version : int
            The new database version.
        """

        logger.info(
            f"Updating database from version {current_version} to {new_version}"
        )
        # TODO add logic to migrate databases between versions

    def add_worker(self, ip: str, active: bool = True):
        pass

    def get_worker(self, ip: str = None) -> List[Worker]:
        """
        Method to get all workers from the database.

        Parameters
        ----------
        ip : str, optional
            The ip of the machine for which to get all workers

        Returns
        -------
        list
            A list of all workers in the database.
        """
        workers = Worker.select()

        if ip:
            return [worker for worker in workers if worker.id.startswith(ip)]
        return workers


if __name__ == "__main__":
    obj = KlinklangDatabase(
        db_type="mariadb",
        database="mydatabase",
        host="localhost",
        user="root",
        password="password",
    )

    print(obj.get_db_version())
    workers = obj.get_worker()
    for worker in workers:
        print(worker.id)
        print(worker.last_seen)
        print(worker.is_active)
    print(obj.get_worker())
    # db.initialize(
    #     MySQLDatabase(
    #         database="mydatabase", host="localhost", user="root", password="password"
    #     )
    # )
    # db.connect()
    # db.create_tables([ServerConfig, Worker, Logs])
    #
    # worker = Worker.create(id="192.168.198.1_5")
    #
    # for a in range(2000):
    #     Logs.create(worker=worker, log=f"Log {a}", id=uuid.uuid4())
