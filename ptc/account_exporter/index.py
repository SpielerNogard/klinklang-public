import datetime
import time

import mysql.connector
import requests
from klinklang.core.config import read_config, AccountExportConfig

from klinklang import logger
from klinklang.core.db_return import db_return

config = read_config()
logger.info("Config loaded")
database_client = config.database.client()
account_table = database_client["accounts"]
stats_table = database_client["stats"]
already_exported_accounts_table = database_client["exported_accounts"]


def get_klinklang_accounts():
    return db_return(account_table.find())


def get_exported_klinklang_accounts():
    return db_return(already_exported_accounts_table.find())


def get_existing_accounts_from_db(export_config: AccountExportConfig) -> set:
    db_connection = mysql.connector.connect(
        host=export_config.host,
        user=export_config.username,
        password=export_config.password,
        database=export_config.db_name,
        port=export_config.port,
    )
    cursor = db_connection.cursor()

    cursor.execute(f"SELECT username FROM {export_config.table_name}")
    existing_usernames = {row[0] for row in cursor.fetchall()}

    cursor.close()
    db_connection.close()
    return existing_usernames


def insert_to_db(export_config, export_candidates):
    logger.info(f"Got {len(export_candidates)} export candidates")

    insert_query = (
        f"INSERT INTO {export_config.table_name} (username, password) VALUES (%s, %s)"
    )

    db_connection = mysql.connector.connect(
        host=export_config.host,
        user=export_config.username,
        password=export_config.password,
        database=export_config.db_name,
        port=export_config.port,
    )
    cursor = db_connection.cursor()

    cursor.executemany(
        insert_query,
        [(account["username"], account["password"]) for account in export_candidates],
    )
    db_connection.commit()
    cursor.close()
    db_connection.close()
    logger.info("Export done")


def get_account_generated_last_hour():
    now = int(time.time())
    stats = db_return(stats_table.find({"name": "generated_accounts"}))
    if not stats:
        return 0
    usable_stats = sorted(
        [stat for stat in stats if stat["time"] >= (now - 3600)],
        key=lambda x: x["time"],
        reverse=True,
    )
    return usable_stats[0]["accounts"] - usable_stats[-1]["accounts"]


def send_discord_message(exported_accounts: int, export_config: AccountExportConfig):
    generated_count = get_account_generated_last_hour()

    if generated_count == 0:
        color = 0xFF0000
    elif generated_count >= 100:
        color = 0x00FF00
    else:
        color = 0xFFFF00

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

    headers = {"Content-Type": "application/json"}
    response = requests.post(export_config.webhook, json=data, headers=headers)
    logger.info(f"Discord notification status: {response.status_code}")


def export_accounts(export_config: AccountExportConfig):
    logger.info(f"Starting account exporter. Used config: {export_config}")
    if export_config is None:
        logger.info("No export config found. Export disabled")
        return

    klinklang_accounts = get_klinklang_accounts()
    db_accounts = get_existing_accounts_from_db(export_config=export_config)

    export_candidates = []
    for account in klinklang_accounts:
        if db_return(
            already_exported_accounts_table.find({"username": account["username"]})
        ):
            print(f"Skipping {account['username']} since it was already exported")
            continue
        username = account["username"]
        if username not in db_accounts:
            export_candidates.append(account)

    insert_to_db(export_config, export_candidates)
    already_exported_accounts_table.insert_many(
        [{"username": account["username"]} for account in export_candidates]
    )

    if export_config.discord is True:
        send_discord_message(
            exported_accounts=len(export_candidates), export_config=export_config
        )


if __name__ == "__main__":
    logger.info(f"Starting account exporter. Used config: {config.export}")

    send = False
    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now.minute == 0:
            if not send:
                export_accounts(export_config=config.export)
                send = True
        else:
            send = False
        time.sleep(1)
