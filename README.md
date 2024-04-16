# klinklang

A new super fast PTC Account generator.

# Setup

## Prequisites
- a linux (tested on ubuntu) x86 system
- python installed
- docker installed with docker compose
- proxies (Only IPAuth is supported)
- 
## SetupProcess
1. install PyYaml `pip install PyYaml`
2. run the config generator `python configgenerator.py`
   - answer all questions from it
   - it will automaticaly start all containers
   - if not run `docker compose up -d`

## Updating
1. Use `docker-compose pull` to pull the latest image versions
2. Use `docker-compose up -d --force-recreate` to restart your docker stack

## Updating if a the config has changed
1. Use `git pull` to get the newest configgenerator
2. Use `python configgenerator.py` to generate a new config and compose
3. Follow #Updating

# Notes
all accounts are stored to the database, we currently have no GUI to access them. So you need a little script to get your accounts from database

every cookie generator can handle 7 Account Generators

with 250 proxies and 2 CookieGenerators and 10 AccountsGenerators we use around 6GB of ram, while generating 10 accounts/sec

```python
import pymongo
from urllib.parse import quote_plus

DATABASE_IP ="YOUR DB IP HERE"
DB_USERNAME = "YOUR DB USERNAME"
DB_PASSWORD = "YOUR DB PASSWORD"
DB_NAME = "YOUR DB NAME"

url = "mongodb://%s:%s@%s" % (
            quote_plus(DB_USERNAME),
            quote_plus(DB_PASSWORD),
            f"{DATABASE_IP}/",
        )

db_client = pymongo.MongoClient(url)
database = db_client[DB_NAME]
account_table = database['accounts']

def db_return(result):
    return [
        {key: value for key, value in item.items() if key not in ["_id"]}
        for item in result
    ]

accounts = db_return(account_table.find())
# format is {'email': 'email', 'username': 'username', 'screenname': 'screenname', 'password': 'password', 'dob': '1994-10-06'}
# print the accounts in RDM format
lines = []
for account in accounts:
    print(account['username'], account['password'])
    lines.append(f"{account['username']}, {account['password']}\n")

with open('accounts.txt','w') as out_file:
    out_file.writelines(lines)
```

# TODOS
- [ ] add a GUI
- [ ] optimize proxy rotation
