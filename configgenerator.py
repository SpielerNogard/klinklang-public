import os
import sys
from copy import deepcopy

import yaml

from klinklang_public.core.config_generation.database_config import get_database_config, get_container_config_from_db_config
from klinklang_public.core.config_generation.domain_config import get_domain_config
from klinklang_public.core.config_generation.mail_reader_config import get_mail_reader_config, \
    get_container_config_from_mail_reader
from klinklang_public.core.config_generation.mail_server_config import get_mail_server_config, \
    get_container_config_from_mail_server
from klinklang_public.core.config_generation.proxy_config import get_proxy_config, get_container_config_from_proxy
from klinklang_public.core.config_generation.queue_config import get_container_config_from_queue_config, get_queue_config

DOCKERCOMPOSE = {
    "version": "3.2",
    "services": {
    },
    "networks": {"klinklang_net": {"driver": "bridge"}},
}


def input_with_default(prompt, default):
    result = input(f"{prompt}({default=})")
    if not result:
        return default
    return result

CONFIGS ={'database':{'container':get_container_config_from_db_config, 'config':get_database_config},
          'queue':{'config':get_queue_config, 'container':get_container_config_from_queue_config},
          'mail_server':{'config':get_mail_server_config, 'container':get_container_config_from_mail_server},
'mail_reader':{'config':get_mail_reader_config, 'container':get_container_config_from_mail_reader},
          'domains':{'config':get_domain_config},
          'proxies':{'config':get_proxy_config, 'container':get_container_config_from_proxy}
          }

base_compose = deepcopy(DOCKERCOMPOSE)
base_config = {}

build= False
if '--build' in sys.argv:
    build = True
print("Welcome to klinklang_public!")
if os.path.isfile("docker-compose.yml") and os.path.exists("config.yml"):
    if (
        input_with_default(
            "Config already found. Do you want to start the service?", default="y"
        )
        == "y"
    ):
        os.system("docker compose up -d --build --force-recreate")
        sys.exit()

for _, config in CONFIGS.items():
    container_logic = config.get('container')
    config_logic = config['config']

    service_config = config_logic()
    base_config.update(service_config)
    if container_logic is not None:
        container_config = container_logic(service_config, build=build)
        base_compose['services'].update(container_config)

with open("config.yml", "w") as ymlfile:
    yaml.dump(base_config, ymlfile)

with open("docker-compose.yml", "w") as ymlfile:
    yaml.dump(base_compose, ymlfile)
#     config = yaml.safe_load(ymlfile)
#
# print(config)
if input_with_default("Do you want to start klinklang_public?", default="y") == "y":
    os.system("docker compose up -d --build --force-recreate")
