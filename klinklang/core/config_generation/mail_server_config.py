from klinklang.core.config_generation.input_with_default import input_with_default


def get_mail_server_config():
    print(f'{"-"*5} MailServer Configurations {"-"*5}')
    if input_with_default("Do you want to run the MailServer?", default="y") == "y":
        port = input_with_default("The MailServer port: ", "25")
        return {'container':True,'mailserver':{ 'port':port}}
    return {'container':False}

def get_container_config_from_mail_server(mail_config, build:bool=False):
    compose =  {"mail_server": {
            "container_name": "klingklang-mail",
            "image": "stctmuel/klinklang-mail-server",
            "extra_hosts": ["host.docker.internal:host-gateway"],
            "ports": [f"{mail_config.get('mailserver',{}).get('port',25)}:25"],
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
        compose = {"mail_server": {
            "container_name": "klingklang-mail",
            "build": {"context": ".", "dockerfile": "mail_server/Dockerfile"},
            "extra_hosts": ["host.docker.internal:host-gateway"],
            "ports": [f"{mail_config.get('mailserver', {}).get('port', 25)}:25"],
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
    return compose if mail_config['container'] is True else {}