import uuid

from klinklang.core.logger import Logger
from klinklang.core.models.worker import Worker
from klinklang.server.database import KlinklangDatabase

logger = Logger("Server")


class KlinkklangServer:
    def __init__(self):
        self._db = KlinklangDatabase(
            db_type="mariadb",
            database="mydatabase",
            host="localhost",
            user="root",
            password="password",
        )

    def add_worker(self, ip: str):
        logger.info(f"{ip} is requesting a new worker")
        workers = self._db.get_worker(ip=ip)
        for worker in workers:
            if worker.is_active is False:
                worker.is_active = True
                worker.save()
                logger.info(f"Worker {worker.id} is now active")
                return worker.id
        worker = Worker.create(id=f"{ip}_{uuid.uuid4()}", is_active=True)
        logger.info(f"Worker {worker.id} created and is now active")
        return worker.id

    def start(self):
        logger.info("Starting server")

        # TODO
        # load current state from db
        pass

    def get_config_for_service(self, service: str):
        return self._db.get_server_config(service)


if __name__ == "__main__":
    server = KlinkklangServer()
    server.start()
    print(server.add_worker(ip="192.168.198.22"))
