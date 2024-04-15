from klinklang_public.core.config_generation.input_with_default import input_with_default


def get_export_config():
    print(f'{"-"*5} Export Configurations {"-"*5}')
    export_config = {'export':False}
    export = input_with_default("Do you want to export your accounts to RDM or Dragonite ? [n/y]", default="n")
    if export == 'y':
        destination = 'RDM'
        use_rdm = input_with_default("Do you want to export to RDM? [n/y]", default="n")
        if use_rdm == 'n':
            destination = 'DRAGONITE'
            print('OK dragonite was selected')

        host = input('Please provide the ip of the database, where the accounts should be imported to: ')
        username = input('Please provide the username of this database: ')
        password = input('Please provide the password of this database: ')
        db_name = input('Please provide the name of the database: ')
        table_name = input_with_default("What table name should be used ? ", default="account")
        export_config = {'export': True, 'host':host, 'password':password, 'username':username, 'db_name':db_name, 'table_name':table_name, 'destination':destination}

        activate_discord = input_with_default("Do you want to send messages to Discord with stats? [n/y]", default="n")
        export_config['discord'] = False
        if activate_discord == 'y':
            export_config['discord'] = True
            webhook_url = input('Please provide a webhook url: ')
            export_config['webhook'] = webhook_url

    return {'export':export_config} if export_config['export'] is True else {}


def get_container_config_from_export(export_config, build:bool=False):
    compose =  {"account_exporter": {
            "container_name": "klingklang-account_exporter",
            "image": "stctmuel/klinklang-account_exporter",
            "extra_hosts": ["host.docker.internal:host-gateway"],
            "restart": "unless-stopped",
            "logging": {
                "driver": "json-file",
                "options": {"max-size": "1m", "max-file": "3"},
            },
            "volumes": [
                "./config.yml:/app/config.yml",
            ],
        "networks": ["klinklang_net"],
            "depends_on": ["mongodb"],
        }}
    if build:
        compose = {"account_exporter": {
            "container_name": "klingklang-account_exporter",
            "build": {"context": ".", "dockerfile": "account_exporter/Dockerfile"},
            "extra_hosts": ["host.docker.internal:host-gateway"],
            "restart": "unless-stopped",
            "logging": {
                "driver": "json-file",
                "options": {"max-size": "1m", "max-file": "3"},
            },
            "volumes": [
                "./config.yml:/app/config.yml",
            ],
            "networks": ["klinklang_net"],
            "depends_on": ["mongodb"],
        }}
    return compose if export_config else {}