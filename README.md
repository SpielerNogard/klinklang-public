# klinklang

A new super fast PTC Account generator.

# Setup

## Prequisites
- linux (x86/arm), mac os (x86/arm) or windows (x86) system, the accountgeneration, need a desktop. The dockers can also run headless
- Google Chrome installed
- python installed `python == 3.11`
- docker installed with docker compose
- proxies (Only IPAuth is supported) (Not needed, if you want to use your home ip)

## SetupProcess
1. install PyYaml `pip install PyYaml`
2. run the config generator `python configgenerator.py`
   - answer all questions from it
   - it will automaticaly start all containers
   - if not run `docker compose up -d`
3. install requirements for account_generator `pip install -r account_generation/requirements.txt`
4. create your config.yml `cp account_generation/config.example.yml account_generation/config.yml`
5. edit your config.yml according to your needs for more info see `AccountGenerationConfig` section
6. start account generation `python account_generation/account_generator.py`
7. For your license, ask the discord bot for help `$help` in any channel of our server 

## AccountGenerationConfig
```yaml
database:
  database_name: klinklang
  host: databasehost
  password: mongoadmin
  username: mongodb
domains:
  - domain_name: mail.i-love-imperva.de
proxies:
  - proxy: 123.123.123
    rotating: false
  - proxy: 123.123.124
accounts:
  save_to_file : true
  format: '{email}, {username}, {password}, {dob}'
```
`database` Configuration for your Database Connection
- `database_name` the name of your database
- `host` the host of your database (can be ip or hostname)
- `password` the password of your database
- `username` the username of your database

`domains` Configuration for the domains, which should be used for account generation, this is a list
- `domain_name` the domain_name (the email) example: `mail.i-love-imperva.de` this would generate the mails `{account_name}@mail.i-love-imperva.de`

`proxies` Configuration for your proxies. This part also can be deleted, if the ip of your machine should be used, this is also a list
- `proxy` The ip and port of your proxy example `https://123.123.123.3:9000`
- `rotating` : default `False` if `True` the proxy will not have any cooldown between usages, your proxy provider will handle the rotation

`accounts` Configuration for storing your generated accounts to files
- `save_to_file` : if `True` the accounts will be saved to a file
- `format` : The format in which the accounts should be stored in the file. `{email}` will be replace with the account email, `{username}` with the username, `password` with the password, `{dob}` with the date of birth

Example if your machines ip should be used
```yaml
database:
  database_name: klinklang
  host: databasehost
  password: mongoadmin
  username: mongodb
domains:
  - domain_name: mail.i-love-imperva.de
accounts:
  save_to_file : true
  format: '{email}, {username}, {password}, {dob}'
```

Example if the accounts should only be saved to the database
```yaml
database:
  database_name: klinklang
  host: databasehost
  password: mongoadmin
  username: mongodb
domains:
  - domain_name: mail.i-love-imperva.de
accounts:
  save_to_file : false
  format: '{email}, {username}, {password}, {dob}'
```

## Notes
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

# FAQ

## Mails
### What is the difference between MailReader and MailServer ?
The `MailServer` is an IMAP server, which is hosted on your server. For it to function properly you need to add all
needed MX-Records to your domain, that the server can get emails. You can send a testemail to your domain, and test if the message appears in the logs.
If the received message contains a verification code from PTC, the code will be added to the database for later usage in account activation.
If you use the MailServer you `dont` need the MailReader

The `MailReader` is a service, which can be used if your domain provider already provides you with a mail server. It will login using the provided
username and password to your mail account and will read **all** messages. If the message contains a verification code it will be saved to the database
for later usage in account activation. Messages from niantic will be deleted after they was read.
