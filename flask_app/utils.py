from typing import Dict
from flask import request
import subprocess


def base_url() -> str:
    return request.scheme + '://' + request.host

def client_ip() -> str:
    client_ip = request.headers.get('cf-connecting-ip')
    if client_ip is None:
        client_ip = request.remote_addr
    return client_ip

def get_cluster_status() -> Dict[str, str]:
    # Get the status
    output = subprocess.run(['/scripts/cluster/setup/master/check_status.sh'], stdout=subprocess.PIPE, timeout=10).stdout.decode('utf-8')

    status = {
        'slaves': [],
        'manager': {},
        'mysqld': {}
    }
    section = ''
    # Parse the output
    for line in output.split('\n'):
        if '[ndbd(NDB)]' in line:
            section = 'ndbd'
            continue
        elif '[ndb_mgmd(MGM)]' in line:
            section = 'mgmd'
            continue
        elif '[mysqld(API)]' in line:
            section = 'mysqld'
            continue
        elif section == 'ndbd' and line.startswith('id='):
            print('ndbd: ' + line)
        elif section == 'mgmd' and line.startswith('id='):
            print('mgmd: ' + line)
        elif section == 'mysqld' and line.startswith('id='): 
            print('mysqld: ' + line)
    return status
        
