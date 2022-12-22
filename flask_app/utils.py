from typing import Dict, List
from flask import request, Flask
import subprocess, requests, time


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
            status['slaves'].append('not connected' not in line)
        elif section == 'mgmd' and line.startswith('id='):
            status['manager'] = 'not connected' not in line
        elif section == 'mysqld' and line.startswith('id='): 
            status['mysqld'] = 'not connected' not in line
    return status

def ensure_slaves_are_up(slaves: List[str], hostname: str):
    status = get_cluster_status()
    if len(status['slaves']) < len(slaves) or not all(status['slaves']):
        for i in range(len(slaves)):
            if len(status['slaves']) < len(slaves) or not status['slaves'][i]:
                resp = requests.get(
                    url=f'http://{slaves[i]}/start/{hostname}',
                    timeout=60
                )
                if resp.status_code != 200 or not resp.json()['connected']:
                    return 'An error occured trying to start slave #{}.'.format(i+1)
        # Check if slaves are started, max retries = 10
        all_started = False
        for i in range(10):
            status = get_cluster_status()
            if len(status['slaves']) < len(slaves) or not all(status['slaves']):
                time.sleep(1)
            else:
                all_started = True
                break
        if not all_started:
            return 'One or more slave is unable to connect to the master.'
    return None

def ensure_mysqld_is_up(app: Flask):
    status = get_cluster_status()
    if not status['mysqld']:
        try:
            app.logger.info('Starting mysqld...')
            subprocess.run(['/scripts/cluster/setup/master/start_mysqld.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        except:
            subprocess.run(['killall', 'mysqld'], stdout=subprocess.PIPE)
            return 'Failed to start mysqld.'
        status = get_cluster_status()
        mysqld_started = False
        for i in range(10):
            status = get_cluster_status()
            if not status['mysqld']:
                time.sleep(1)
            else:
                mysqld_started = True
                break
        if not mysqld_started:
            return 'Failed to start mysqld.'
        try:
            app.logger.info('Securing the mysql database...')
            subprocess.run(['/scripts/cluster/setup/master/secure_mysql.sh'], stdout=subprocess.PIPE, timeout=20)
        except:
            subprocess.run(['killall', 'mysqld'], stdout=subprocess.PIPE)
            return 'Failed to secure the mysql installation.'
        try:
            app.logger.info('Adding the database user...')
            subprocess.run(['/scripts/cluster/setup/master/create_myapp_user.sh'], stdout=subprocess.PIPE, timeout=10)
        except:
            subprocess.run(['killall', 'mysqld'], stdout=subprocess.PIPE)
            return 'Failed to create the database user.'
    return None
