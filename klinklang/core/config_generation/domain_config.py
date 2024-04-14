from klinklang.core.config_generation.input_with_default import input_with_default


def get_domain_config():
    print(f'{"-"*5} Domain Configurations {"-"*5}')
    domain_config ={'domains':[]}

    domain_name = input('Please provide your domain name: ')
    domain_name = domain_name.replace('@','')
    domain_config['domains'].append({'domain_name':domain_name})
    more = input_with_default("Do you want to add more domains [n/y]", default="n")
    while more == 'y':
        domain_name = input('Please provide your domain name: ')
        domain_name = domain_name.replace('@', '')
        domain_config['domains'].append({'domain_name': domain_name})
        more = input_with_default("Do you want to add more domains [n/y]", default="n")
    return {'domains':domain_config}