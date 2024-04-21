# klinklang

A new super fast PTC Account generator.

# Setup

## Prequisites
- a linux (tested on ubuntu) x86 system
- python installed `python >= 3.8`
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

# FAQ

## Proxies
### What proxies are supported ?
We should support nearly every proxy provider. They need to be provided in a file `proxies.txt` with one proxy per line
Supported Authentication Methods are: 
1. IP-Authorization
   every line should be `{ip}:{port}`
   for example: `104.143.224.13:5874`
2. Username/Password
   every line should be `{username}:{password}@{ip}:{port}`
   for example: `username:password@104.143.224.13:5874`
   
   !!Attention!! this does not work any longer

### My proxy provider provides me with own proxy rotation and unlimited proxies. What to do ? 
first disable the proxy check in your `config.yml`. Now you can add the proxy endpoint to your proxies.txt but this time
you add ad `/unlimited` behind it. For example `104.143.224.13:5874/unlimited` or `username:password@104.143.224.13:5874/unlimited`.
You can mix both unlimited and normal proxies

## Mails
### What is the difference between MailReader and MailServer ?
The `MailServer` is an IMAP server, which is hosted on your server. For it to function properly you need to add all
needed MX-Records to your domain, that the server can get emails. You can send a testemail to your domain, and test if the message appears in the logs.
If the received message contains a verification code from PTC, the code will be added to the database for later usage in account activation.
If you use the MailServer you `dont` need the MailReader

The `MailReader` is a service, which can be used if your domain provider already provides you with a mail server. It will login using the provided
username and password to your mail account and will read **all** messages. If the message contains a verification code it will be saved to the database
for later usage in account activation. Messages from niantic will be deleted after they was read.
