from klinklang_public.core.config_generation.input_with_default import input_with_default


def get_mail_reader_config():
    print(f'{"-"*5} MailReader Configurations {"-"*5}')
    if input_with_default("Do you want to run the MailReader?", default="y") == "y":
        mail_boxes = []

        username = input("The username for the email: ")
        password = input("The password for the email: ")
        imap_server = input_with_default("The IMAP server: ", "imap.strato.de")
        mail_boxes.append(
            {"username": username, "password": password, "imap_server": imap_server}
        )
        more = input_with_default("Do you want to add more mail_boxes?", default="n")
        while more == "y":
            username = input("The username for the email: ")
            password = input("The password for the email: ")
            imap_server = input_with_default("The IMAP server: ", "imap.strato.de")
            mail_boxes.append(
                {"username": username, "password": password, "imap_server": imap_server}
            )

        return {'container':True, 'mailreader':{'mailbox':mail_boxes}}
    return {'container':False}

def get_container_config_from_mail_reader(mail_config, build:bool=False):
    compose =  {"mail_reader": {
            "container_name": "klingklang-mail-reader",
            "image": "stctmuel/klinklang_public-mail-reader",
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
        compose = {"mail_reader": {
            "container_name": "klingklang-mail-reader",
            "build": {"context": ".", "dockerfile": "mail_reader/Dockerfile"},
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
    return compose if mail_config['container'] is True else {}