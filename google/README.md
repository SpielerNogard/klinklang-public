A Google Account Generator

## Requirements
- Python 3.11 or higher
- a SMSPool API key (https://www.smspool.net/)
- Optional Proxies (both basic auth or user/pass are supported)

## Installation
1. Clone the repository
2. Install the klinklang python package `pip install ptc` (from repo root)
3. Install the requirements `pip install -r requirements.txt` (from google folder)
4. Edit the `config.yml` in the google folder according to your needs
5. Run the script `python index.py` (from google folder)

The accounts get stored in a file called `gmail_accounts.txt` in the google folder.
the prices for SMS can vary greatly, I have seen everything from 1 cent to 100 cents. A limit for this has yet to be implemented. However, if you have enough credit, you can generate an account very quickly

## TODOs
- [ ] Add more sms providers
- [ ] Add limits for the costs of the sms