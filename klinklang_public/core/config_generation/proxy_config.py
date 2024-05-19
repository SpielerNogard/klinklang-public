from klinklang_public.core.config_generation.input_with_default import input_with_default
import os

def get_proxy_config():
    print(f'{"-"*5} Proxy Configurations {"-"*5}')
    exists =os.path.isfile('proxies.txt')
    while not exists:
        input('Please create a proxies.txt with your proxies. (1 per line) and press enter')
        exists = os.path.isfile('proxies.txt')

    check_before = input_with_default("Do you want to check your proxies before running?", default="y")
    check_before = True if check_before == 'y' else False
    cookie_workers = input_with_default("How much workers do you want to use for cookie generation?", default="1")
    account_workers = input_with_default("How much workers do you want to use for account generation?", default="1")
    return {'proxies':{ 'use_free':False, 'check_before_usage':check_before}, 'account_workers':account_workers, 'cookie_workers':cookie_workers}

def get_container_config_from_proxy(config, build:bool=False):
    compose =  {#"proxy_rotation": {
    #         "container_name": "klingklang-proxy-handler",
    #         "image": "stctmuel/klinklang-proxy-rotation",
    #         "extra_hosts": ["host.docker.internal:host-gateway"],
    #         "restart": "unless-stopped",
    #         "logging": {
    #             "driver": "json-file",
    #             "options": {"max-size": "1m", "max-file": "3"},
    #         },
    #         "volumes": [
    #             "./config.yml:/app/config.yml",
    #             "./proxies.txt:/app/proxies.txt",
    #         ],
    #     "networks": ["klinklang_net"],
    #         "depends_on": ["mongodb", "rabbitmq"],
    #     },
    #     "cookie_generation": {
    #         "image": "stctmuel/klinklang-cookie-generation",
    #         "extra_hosts": ["host.docker.internal:host-gateway"],
    #         "restart": "unless-stopped",
    #         "logging": {
    #             "driver": "json-file",
    #             "options": {"max-size": "1m", "max-file": "3"},
    #         },
    #         "volumes": [
    #             "./config.yml:/app/config.yml",
    #         ],
    #         "networks": ["klinklang_net"],
    #         "depends_on": ["mongodb", "rabbitmq"],
    #         'deploy':{'mode':'replicated', 'replicas':config['cookie_workers']}
    #     },
    #     "account_generation": {
    #         "image": "stctmuel/klinklang-account-creation",
    #         "extra_hosts": ["host.docker.internal:host-gateway"],
    #         "restart": "unless-stopped",
    #         "logging": {
    #             "driver": "json-file",
    #             "options": {"max-size": "1m", "max-file": "3"},
    #         },
    #         "volumes": [
    #             "./config.yml:/app/config.yml",
    #         ],
    #         "networks": ["klinklang_net"],
    #         "depends_on": ["mongodb", "rabbitmq"],
    #         'deploy': {'mode': 'replicated', 'replicas': config['account_workers']}
    #     },
        "stats_collector": {
            "image": "stctmuel/klinklang-stats_collector",
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
            "depends_on": ["mongodb", "rabbitmq"],
        }
    }
    if build:
        compose = {#"proxy_rotation": {
        #     "container_name": "klingklang-proxy-handler",
        #     "build": {"context": ".", "dockerfile": "proxy_rotation/Dockerfile"},
        #     "extra_hosts": ["host.docker.internal:host-gateway"],
        #     "restart": "unless-stopped",
        #     "logging": {
        #         "driver": "json-file",
        #         "options": {"max-size": "1m", "max-file": "3"},
        #     },
        #     "volumes": [
        #         "./config.yml:/app/config.yml",
        #         "./proxies.txt:/app/proxies.txt",
        #     ],
        #     "networks": ["klinklang_net"],
        #     "depends_on": ["mongodb", "rabbitmq"],
        # },
        #     "cookie_generation": {
        #         "build": {"context": ".", "dockerfile": "cookie_generation/Dockerfile"},
        #         "extra_hosts": ["host.docker.internal:host-gateway"],
        #         "restart": "unless-stopped",
        #         "logging": {
        #             "driver": "json-file",
        #             "options": {"max-size": "1m", "max-file": "3"},
        #         },
        #         "volumes": [
        #             "./config.yml:/app/config.yml",
        #         ],
        #         "networks": ["klinklang_net"],
        #         "depends_on": ["mongodb", "rabbitmq"],
        #         'deploy': {'mode': 'replicated', 'replicas': config['cookie_workers']}
        #     },
        #     "account_generation": {
        #         "build": {"context": ".", "dockerfile": "account_generation/Dockerfile"},
        #         "extra_hosts": ["host.docker.internal:host-gateway"],
        #         "restart": "unless-stopped",
        #         "logging": {
        #             "driver": "json-file",
        #             "options": {"max-size": "1m", "max-file": "3"},
        #         },
        #         "volumes": [
        #             "./config.yml:/app/config.yml",
        #         ],
        #         "networks": ["klinklang_net"],
        #         "depends_on": ["mongodb", "rabbitmq"],
        #         'deploy': {'mode': 'replicated', 'replicas': config['account_workers']}
        #     },
            "stats_collector": {
                "build": {"context": ".", "dockerfile": "stats_collector/Dockerfile"},
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
                "depends_on": ["mongodb", "rabbitmq"],
            }
        }

    return compose