from klinklang.core.logger import Logger
from klinklang.core.models.worker import Worker


class KlinkklangServer:
    def __init__(self):
        self._logger = Logger("Server")
        self._workers = []
        pass

    def add_worker(self, worker: Worker):
        self._logger.info(f"Adding worker {worker.id}")

    def start(self):
        self._logger.info("Starting server")

        # TODO
        # load current state from db
        pass
