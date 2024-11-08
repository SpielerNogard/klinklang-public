import datetime
import threading
import time

from klinklang import logger
from klinklang.core.config import read_config
from klinklang.core.db_return import db_return

config = read_config()
logger.info("Config loaded")
database_client = config.database.client()
logger.info("Connected to database")


def collect_account_stats():
    account_table = database_client['accounts']
    stats_table = database_client['stats']
    while True:
        logger.info('Collecting Account stats')
        accounts = db_return(account_table.find())
        stats_table.insert_one({'time':int(time.time()), 'accounts':len(accounts), 'name':'generated_accounts'})
        logger.info(f'Generated Accounts: {datetime.datetime.now(datetime.timezone.utc).isoformat()} {len(accounts)}')
        time.sleep(60)


if __name__ =="__main__":
    threading.Thread(target=collect_account_stats).start()

    while True:
        time.sleep(60000)