
# Klinklang

A new, super-fast PTC account generator


## Setup
The Klinklang stack consists of a MongoDB database, a Stats collector, a mail reader/server, and the account_generation Python script. The account_generation script gets run outside of Docker while the rest of the components are separated into their own Docker containers.

### Requirements
The Docker containers and the account_generation script can run on separate hosts or on the same host. Each host has its own requirements, if using one host for all components you must meet all requirements:
1. Linux (x86/ARM), Mac OS (x86/ARM), or Windows (x86) are supported
   - The Docker containers can run headless
   - The account_generation script requires a desktop environment despite running headless
2. Host running account_generation script:
   - Google Chrome installed on host OS
   - Python 3.11
     - pip
3. Host running Docker containers:
   - Docker, with Docker components
4*Optional:* Proxies (Basic Auth and IP Auth supported, see [FAQ](#can-i-use-basicauth-for-my-proxies))

### Initial Setup

#### Server Preparation
1. Edit the config.yml file in this directory according to your needs (see [KlinklangStack Config](#KlinklangStack Config) for more info)
2. Start the docker containers with `docker compose up -d`
#### Account Generation Preparation
1. install klinklang package: `pip install .` (inside this directory)
2. Install additional requirements for account_generation script host: `pip install -r account_generation/requirements.txt`
3. Edit the config.yml file in the account_generation directory according to your needs (see [AccountGeneration Config](#accountgeneration-config) for more info) 
4. Run the account_generation script with `python account_generation/index.py`

## KlinklangStack Config
Example config.yml with default values:
```yaml
database:
  database_name: klinklang
  host: mongodb
  password: mongoadmin
  username: mongodb
mailreader:
  mailbox:
  - imap_server: imap.strato.de
    password: test
    username: test
mailserver:
  port: '25'
exporter:
   rate: 3600
   destination: DRAGONITE
   discord: false
   webhook: 'https://my-discord-webhook-url'
   host: my-dragonite_host
   password: my-dragonite_password
   username: my-dragonite_username
   db_name: my-dragonite_db
   table_name: my-dragonite_table
   port: 3306
```
#### Details: <sup>(* = *required*)</sup>
1. *`database`: Configuration for your Database Connection (the mongo db one)
   - `database_name`: the name of your database
   - `host`: the host of your database (can be ip or hostname)
   - `password`: the password of your database
   - `username`: the username of your database
2. `mailreader`: Configuration for the mail reader service, if not given the service is disabled
   - `mailbox`: a list of mail boxes to which the reader should connect
     - `imap_server`: the imap server of your mail provider
     - `password`: the password of your mail account
     - `username`: the username of your mail account
3. `mailserver`: Configuration for the mailserver service, if not given the service is disabled
   - `port`: the port inside the container on which the mailserver should listen
   - `host`: the host inside the container on which the mailserver should listen
4. `exporter`: Configuration for the service, which exports all accounts to either Dragonite or RDM. if not given the service is disabled
   - `rate`: the rate at which the exporter should export the accounts
   - `destination`: the destination of the accounts, either `DRAGONITE` or `RDM`
   - `discord`: if set to true the exporter will send a message to a discord webhook
   - `webhook`: the discord webhook to which the exporter should send the message
   - `host`: the host of the database to which the exporter should connect
   - `password`: the password of the database to which the exporter should connect
   - `username`: the username of the database to which the exporter should connect
   - `db_name`: the name of the database to which the exporter should connect
   - `table_name`: the name of the table to which the exporter should connect
   - `port`: the port of the database to which the exporter should connect
## AccountGeneration Config
Example config.yml with default values:
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
proxy_file: proxies.txt
show_total_accounts: false
headless : true
account_password : 'MYFancyPassword99#'
mail_prefix: my_fancy_prefix
proxy_region: Germany
random_subdomain: true
subdomain_length: 32
proxy_cooldown : 1900
binary_location: ''
```
#### Details: <sup>(* = *required*)</sup>

1. *`database`: Configuration for your Database Connection
   - `database_name`: the name of your database
   - `host`: the host of your database (can be ip or hostname)
   - `password`: the password of your database
   - `username`: the username of your database

2. *`domains`: Configuration for the domains, which should be used for account generation, this is a list
   - `domain_name`: the domain used for emails, example: `mail.i-love-imperva.de` would generate emails with format `{account_name}@mail.i-love-imperva.de`

3. *`proxies`: List of proxies to use. Not required if using proxy_file or if not using proxies at all
   - `proxy`: The ip and port of your proxy example `https://123.123.123.3:9000`
   - `rotating`: default `False`, if `True` the proxy will not have any cooldown between usages, your proxy provider will handle the rotation

4. *`accounts`: Configuration for storing your generated accounts to files
   - `save_to_file`: if `True` the accounts will be saved to a file
   - `format`: The format in which the accounts should be stored in the file. `{email}` will be replace with the account email, `{username}` with the username, `password` with the password, `{dob}` with the date of birth, `{region}` will be replaced with the region

5. *`proxy_file`: The name of the file containing a list of proxies to use. Not required if using proxies list in config or not using proxies at all
   - format is `ip:port` or `user:pass@host:port`. If you add a `/rotating` behind the proxy it will be marked as rotating, for example: `ip:port/rotating`

6. `show_total_accounts`: if set to true, will display the total count of generated accounts after each generation attempt

7. `headless`: `true` is the default, set it to `false` if you want to see the browser window, nice for debugging

8. `account_password`: if set all accounts will have the same password, if not a new random password will be generated

9. `mail_prefix`: if set klinklang will generate accounts using the plus technique. This will generate emails like `{prefix}+{username}@{domain}`

10. `proxy_region`: if set klinklang will not attempt to auto-detect the region of the proxy, it will use the defined region for account information

11. `random_subdomain`: if set to true, klinklang will generate random subdomains for every account, for this your domain should support a catch all (e.g. `true` results in `randomsubdomain.i-love-imperva.de`)

12. `subdomain_length`: set a custom length for random subdomains, if enabled

13. `proxy_cooldown`: default 1900, the cooldown between the usage of the proxies in seconds. Decreasing this will increase the risk of your proxies getting blocked but increases the potential speed at which you can create accounts.

14. `binary_location`: if set the defined binary will be used instead of the installed chrome version. For example if you have both Google Chrome and Brave installed on your mac (Chrome as default browser) and you want to use Brave you would add to your config `binary_location: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'`

15. `email_code_waiting_max`: set the max attempts for waiting for the code from the email, default is 180
## FAQ

#### What is the difference between MailReader and MailServer?
MailServer is an IMAP server (mailserver) that you host yourself. For it to function properly you need to add all needed MX-Records to your domain so that the server can get emails. You can send a test email to your domain, and test if the message appears in the logs. If the received message contains a verification code from PTC, the code will be added to the database for later usage in account activation.

MailReader is a service which can be used to read emails from a provider, e.g. if your domain provider already provides you with a mail server. It will login using the provided username and password to your mail account and will read all messages. If the message contains a verification code it will be saved to the database for later usage in account activation. Messages from niantic will be deleted after they are read.

You need one or the other, *not both*.

#### Do I need to host a database just for Klinklang?
No. One of the included Docker containers is a MongoDB container which is already set up as needed - just customize your configuration files and start it up.

#### What should I set for account_workers and cookie_workers?
These settings can be ignored, they are left over from previous code and are not used. 

#### What proxy provider should I use?
This is something that is generally kept secret as higher usage increases the chance of the proxy being banned. Based on user reports in Discord, Webshare is generally banned. Residential proxies are often considered "better" when it comes to not being banned already however this is anecdotal.

#### Can I use BasicAuth for my proxies?
While technically supported most users report this does not work for them. If you want to try using BasicAuth make sure you use the format `USER:PASS@IP:PORT`

#### Can I run the account_generation script in PM2?
Yes. It is suggested you set your license in your config, then you can `pm2 start` as normal. If you need to specify your Python interpreter / if using venv just include the `--interpreter` flag.

Example: `pm2 start path/account_generator.py --name klinklang --interpreter /path/to/venv/bin/python`


## Common Issues

#### Python error mentioning `undefined symbol`
Wrong Python version in use, make sure you are using Python 3.11

#### Python error `ModuleNotFoundError`
Reinstall requirements: `pip install -r account_generation/requirements.txt`

