from klinklang.core.config_generation.input_with_default import input_with_default


def get_database_config():
    print(f'{"-" * 5} Database Configurations {"-" * 5}')
    if input_with_default("Do you want to run the database? [n/y]", default="y") == "y":
        container =True
        host = 'mongodb'
    else:
        container = False
        host = input('Please provide your database host ip: ')


    username = input_with_default("The database username: ", "mongodb")
    password = input_with_default("The database password: ", "mongoadmin")
    database_name = input_with_default("The database name: ", "klinklang")

    return {'container':container, 'database':{'host':host, 'username':username, 'password':password, 'database_name':database_name}}

def get_container_config_from_db_config(database_config:dict, build:bool=False):

    compose = {"mongodb": {
        "image": "mongo:6-jammy",
        "container_name": "klinklang-database",
        "ports": ["27017:27017"],
        "volumes": ["./database:/data/db"],
        "networks": ["klinklang_net"],
        "environment": {
            "MONGO_INITDB_ROOT_USERNAME": database_config['database']['username'],
            "MONGO_INITDB_ROOT_PASSWORD": database_config['database']['password'],
        },
        "restart": "unless-stopped",
        "logging": {
            "driver": "json-file",
            "options": {"max-size": "1m", "max-file": "3"},
        },
    }}

    return compose if database_config['container'] is True else {}