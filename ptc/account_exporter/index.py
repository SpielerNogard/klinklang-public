import datetime
import time

import mysql.connector
import requests
from klinklang.core.config import read_config, AccountExportConfig

from klinklang import logger
from klinklang.core.db_return import db_return

# Load configuration
config = read_config()
logger.info("Config loaded")
database_client = config.database.client()
account_table = database_client["accounts"]
stats_table = database_client["stats"]
already_exported_accounts_table = database_client["exported_accounts"]

# Function to fetch accounts from MongoDB
def get_klinklang_accounts():
    return db_return(account_table.find())

# Function to fetch already exported accounts
def get_exported_klinklang_accounts():
    return db_return(already_exported_accounts_table.find())


# Function to get existing accounts from MariaDB
def get_existing_accounts_from_db(export_config: AccountExportConfig) -> set:
    db_connection = mysql.connector.connect(
        host=export_config.host,
        user=export_config.username,
        password=export_config.password,
        database=export_config.db_name,
        port=export_config.port,
    )
    cursor = db_connection.cursor()

    # Query existing accounts from the specified table
    cursor.execute(f"SELECT username FROM {export_config.table_name}")
    existing_usernames = {row[0] for row in cursor.fetchall()}

    cursor.close()
    db_connection.close()
    return existing_usernames


# Function to insert accounts into MariaDB
def insert_to_db(export_config, export_candidates):
    logger.info(f"Got {len(export_candidates)} export candidates")

    insert_query = (
        #f"INSERT INTO {export_config.table_name} (username, password, last_released) "
        #f"VALUES (%s, %s, %s)"
        f"INSERT INTO {export_config.table_name} (username, password) "
        f"VALUES (%s, %s)"
    )

    db_connection = mysql.connector.connect(
        host=export_config.host,
        user=export_config.username,
        password=export_config.password,
        database=export_config.db_name,
        port=export_config.port,
    )
    cursor = db_connection.cursor()

    # Insert the export candidates
    cursor.executemany(
        insert_query,
        #[(account["username"], account["password"], 1) for account in export_candidates],
        [(account["username"], account["password"]) for account in export_candidates],
    )
    db_connection.commit()
    cursor.close()
    db_connection.close()
    logger.info("Export done")


# Function to get the number of accounts generated in the last hour
def get_account_generated_last_hour():
    now = int(time.time())
    stats = db_return(stats_table.find({"name": "generated_accounts"}))
    if not stats:
        logger.info("No stats found for 'generated_accounts'. Returning 0.")
        return 0

    usable_stats = sorted(
        [stat for stat in stats if stat["time"] >= (now - 3600)],
        key=lambda x: x["time"],
        reverse=True,
    )

    if len(usable_stats) < 2:
        logger.info("Not enough stats to calculate accounts generated in the last hour. Returning 0.")
        return 0

    return usable_stats[0]["accounts"] - usable_stats[-1]["accounts"]


# Function to send a Discord notification
def send_discord_message(exported_accounts: int, export_config: AccountExportConfig):
    generated_count = get_account_generated_last_hour()

    if generated_count == 0:
        color = 0xFF0000
    elif generated_count >= 100:
        color = 0x00FF00
    else:
        color = 0xFFFF00

    # Build the Discord message payload
    data = {
        "content": "",
        "username": "Klinklang",
        "avatar_url": "https://github.com/GhostTalker/icons/blob/main/PoGo/klingKlang_favicon.png?raw=true",
        "embeds": [
            {
                "title": "Klinklang Status Report",
                "color": color,
                "thumbnail": {
                    "url": "https://github.com/GhostTalker/icons/blob/main/PoGo/dbsync2.png?raw=true"
                },
                "fields": [
                    {
                        "name": "Created Acc via KlingKlang",
                        "value": str(generated_count),
                        "inline": True,
                    },
                    {
                        "name": f"Synced with {export_config.destination}",
                        "value": str(exported_accounts),
                        "inline": True,
                    },
                ],
                "description": f"Hourly sync from Klinklang to {export_config.destination} completed successfully.",
                "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            }
        ],
    }

    # Send the payload to Discord
    headers = {"Content-Type": "application/json"}
    response = requests.post(export_config.webhook, json=data, headers=headers)
    logger.info(f"Discord notification status: {response.status_code}")

# Function to export accounts from MongoDB to MariaDB
def export_accounts(export_config: AccountExportConfig, limit=None, dry_run=False):
    """
    Export accounts from MongoDB to MariaDB.

    Args:
        export_config (AccountExportConfig): Configuration for database export.
        limit (int, optional): Limit on the number of accounts to process. Default is None (all accounts).
        dry_run (bool): If True, simulate the export without writing to any database. Default is False.
    """
    logger.info(f"Starting account exporter. Config: {export_config}, dry run: {dry_run}")

    if export_config is None:
        logger.info("No export config found. Export disabled")
        return

    # Step 1: Retrieve accounts
    klinklang_accounts = list(get_klinklang_accounts())
    if limit:
        klinklang_accounts = klinklang_accounts[:limit]
    logger.info(f"Fetched {len(klinklang_accounts)} accounts from Klinklang")

    # Step 2: Retrieve already-exported and existing accounts
    exported_accounts = {
        doc["username"] for doc in db_return(already_exported_accounts_table.find())
    }
    logger.info(f"Fetched {len(exported_accounts)} already-exported accounts from MongoDB")

    db_accounts = get_existing_accounts_from_db(export_config=export_config)
    logger.info(f"Fetched {len(db_accounts)} accounts from MariaDB")

    # Step 3: Identify export candidates
    export_candidates = [
        account for account in klinklang_accounts
        if account["username"] not in exported_accounts and account["username"] not in db_accounts
    ]
    logger.info(f"Identified {len(export_candidates)} export candidates")

    if dry_run:
        # Dry run: Log candidates and return
        logger.info(f"Sample export candidates: {export_candidates[:5]}")
    else:
        # Real export: Write to databases
        if export_candidates:
            insert_to_db(export_config, export_candidates)
            already_exported_accounts_table.insert_many(
                [{"username": account["username"]} for account in export_candidates]
            )
            logger.info("Export completed successfully")
        else:
            logger.info("No candidates to export. Skipping database writes.")

    # Always send a Discord notification
    logger.info("Sending Discord message")
    send_discord_message(
        exported_accounts=len(export_candidates), export_config=export_config
    )

    return


if __name__ == "__main__":
    logger.info(f"Starting account exporter. Used config: {config.export}")

    send = False
    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now.minute == 0:
            if not send:
                export_accounts(export_config=config.export)
                #dev_export_accounts(export_config=config.export)
                send = True
        else:
            send = False
        time.sleep(1)
