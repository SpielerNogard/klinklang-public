from klinklang_public.core.config_generation.input_with_default import input_with_default


def get_queue_config():
    print(f'{"-" * 5} Queue Configurations {"-" * 5}')
    if input_with_default("Do you want to run the queue?", default="y") == "y":
        container =True
        host = 'rabbitmq'
    else:
        container = False
        host = input_with_default("The queue host: ", "rabbitmq")


    username = input_with_default("The queue username: ", "guest")
    password = input_with_default("The queue password: ", "guest")

    return {'container':container,'queue':{'username':username, 'password':password, 'host':host}}

def get_container_config_from_queue_config(queue_config:dict, build:bool=False):

    compose = {
        "rabbitmq": {
            "image": "rabbitmq:3-management-alpine",
            "container_name": "klinklang_public-queue",
            "ports": ["5672:5672", "15672:15672"],
            "volumes": [
                ".queue/data/:/var/lib/rabbitmq/",
                ".queue/log/:/var/log/rabbitmq",
            ],
            "environment": {
                "RABBITMQ_DEFAULT_USER": queue_config['queue']['username'],
                "RABBITMQ_DEFAULT_PASS": queue_config['queue']['password'],
            },
            "networks": ["klinklang_net"],
            "restart": "unless-stopped",
            "logging": {
                "driver": "json-file",
                "options": {"max-size": "1m", "max-file": "3"},
            },
        }}

    return compose if queue_config['container'] is True else {}