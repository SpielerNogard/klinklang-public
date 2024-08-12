
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
     - PyYAML (`pip install pyYaml`)
3. Host running Docker containers:
   - Docker, with Docker components
4. Klinklang license (`$help` in any channel in the Klinklang Discord server)
5. *Optional:* Proxies (Basic Auth and IP Auth supported, see [FAQ](#can-i-use-basicauth-for-my-proxies))

### Initial Setup
1. Install additional requirements for account_generation script host: `pip install -r account_generation/requirements.txt`
2. Create and customize configurations: `python configgenerator.py`
   - Answer all questions, it will create your configs based on your answers
3. Create config for account_generation script: `cp account_generation/config.example.yml account_generation/config.yml`
4. Edit config.yml from the previous step according to your needs (see [AccountGeneration Config](#accountgeneration-config) for more info)
5. Start Docker containers if not started (`docker compose up -d`). Start Account Generation script (`python account_generation/account_generator.py`)

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
license: my_fancy_license
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

6. *`license`: Your license key, if not given the program will give you a prompt

7. `show_total_accounts`: if set to true, will display the total count of generated accounts after each generation attempt

8. `headless`: `true` is the default, set it to `false` if you want to see the browser window, nice for debugging

9. `account_password`: if set all accounts will have the same password, if not a new random password will be generated

10. `mail_prefix`: if set klinklang will generate accounts using the plus technique. This will generate emails like `{prefix}+{username}@{domain}`

11. `proxy_region`: if set klinklang will not attempt to auto-detect the region of the proxy, it will use the defined region for account information

12. `random_subdomain`: if set to true, klinklang will generate random subdomains for every account, for this your domain should support a catch all (e.g. `true` results in `randomsubdomain.i-love-imperva.de`)

13. `subdomain_length`: set a custom length for random subdomains, if enabled

14. `proxy_cooldown`: default 1900, the cooldown between the usage of the proxies in seconds. Decreasing this will increase the risk of your proxies getting blocked but increases the potential speed at which you can create accounts.

15. `binary_location`: if set the defined binary will be used instead of the installed chrome version. For example if you have both Google Chrome and Brave installed on your mac (Chrome as default browser) and you want to use Brave you would add to your config `binary_location: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'`

16. `email_code_waiting_max`: set the max attempts for waiting for the code from the email, default is 180
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

