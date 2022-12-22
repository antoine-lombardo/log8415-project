from typing import Dict, List
from flask import request
import subprocess, requests, time, logging, os, json, paramiko, io, sqlparse



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

def ensure_mysqld_is_up():
    status = get_cluster_status()
    if not status['mysqld']:
        try:
            logging.info('Starting mysqld...')
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
            logging.info('Securing the mysql database...')
            subprocess.run(['/scripts/cluster/setup/master/secure_mysql.sh'], stdout=subprocess.PIPE, timeout=20)
        except:
            subprocess.run(['killall', 'mysqld'], stdout=subprocess.PIPE)
            return 'Failed to secure the mysql installation.'
        try:
            logging.info('Adding the database user...')
            subprocess.run(['/scripts/cluster/setup/master/create_myapp_user.sh'], stdout=subprocess.PIPE, timeout=10)
        except:
            subprocess.run(['killall', 'mysqld'], stdout=subprocess.PIPE)
            return 'Failed to create the database user.'
    return None

def clean_db():
    try:
        logging.info('Cleaning database...')
        subprocess.run(['/scripts/cluster/benchmark/clean_db.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    except:
        return 'Failed to clean database.'
    return None

def parse_benchmark(lines: List[str]) -> Dict:
    output = {
        'sql_statistics': {
            'queries_performed': {
                'read': None,
                'write': None,
                'other': None,
                'total': None
            },
            'transactions': None,
            'transactions_per_sec': None,
            'queries': None,
            'queries_per_sec': None,
            'ignored_errors': None,
            'ignored_errors_per_sec': None,
            'reconnects': None,
            'reconnects_per_sec': None
        },
        'general_statistics': {
            'total_time': None,
            'total_number_of_events': None
        },
        'latency': {
            'min': None,
            'avg': None,
            'max': None,
            '95th_percentile': None,
            'sum': None
        },
        'threads_fairness': {
            'events_avg': None,
            'events_stddev': None,
            'execution_time_avg': None,
            'execution_time_stddev': None
        }
    }
    section = None
    for line in lines:
        if 'SQL statistics:' in line:
            section = 'sql_stats'
        elif 'General statistics:' in line:
            section = 'gen_stats'
        elif 'Latency (ms):' in line:
            section = 'latency'
        elif 'Threads fairness:' in line:
            section = 'threads'
        elif section == 'sql_stats':
            if 'read:' in line:
                output['sql_statistics']['queries_performed']['read'] = int(line.replace('read:', '').strip())
            elif 'write:' in line:
                output['sql_statistics']['queries_performed']['write'] = int(line.replace('write:', '').strip())
            elif 'other:' in line:
                output['sql_statistics']['queries_performed']['other'] = int(line.replace('other:', '').strip())
            elif 'total:' in line:
                output['sql_statistics']['queries_performed']['total'] = int(line.replace('total:', '').strip())
            elif 'transactions:' in line:
                sub_line = line.replace('transactions:', '').strip()
                output['sql_statistics']['transactions'] = int(sub_line[:sub_line.index('(')].strip())
                output['sql_statistics']['transactions_per_sec'] = float(sub_line[sub_line.index('(')+1:sub_line.index('per sec')].strip())
            elif 'queries:' in line:
                sub_line = line.replace('queries:', '').strip()
                output['sql_statistics']['queries'] = int(sub_line[:sub_line.index('(')].strip())
                output['sql_statistics']['queries_per_sec'] = float(sub_line[sub_line.index('(')+1:sub_line.index('per sec')].strip())
            elif 'ignored errors:' in line:
                sub_line = line.replace('ignored errors:', '').strip()
                output['sql_statistics']['ignored_errors'] = int(sub_line[:sub_line.index('(')].strip())
                output['sql_statistics']['ignored_errors_per_sec'] = float(sub_line[sub_line.index('(')+1:sub_line.index('per sec')].strip())
            elif 'reconnects:' in line:
                sub_line = line.replace('reconnects:', '').strip()
                output['sql_statistics']['reconnects'] = int(sub_line[:sub_line.index('(')].strip())
                output['sql_statistics']['reconnects_per_sec'] = float(sub_line[sub_line.index('(')+1:sub_line.index('per sec')].strip())
        elif section == 'gen_stats':
            if 'total time:' in line:
                output['general_statistics']['total_time'] = float(line.replace('total time:', '').replace('s', ''))
            elif 'total number of events:' in line:
                output['general_statistics']['total_number_of_events'] = int(line.replace('total number of events:', ''))
        elif section == 'latency':
            if 'min:' in line:
                output['latency']['min'] = float(line.replace('min:', ''))
            elif 'avg:' in line:
                output['latency']['avg'] = float(line.replace('avg:', ''))
            elif 'max:' in line:
                output['latency']['max'] = float(line.replace('max:', ''))
            elif '95th percentile:' in line:
                output['latency']['95th_percentile'] = float(line.replace('95th percentile:', ''))
            elif 'sum:' in line:
                output['latency']['sum'] = float(line.replace('sum:', ''))
        elif section == 'threads':
            if 'events (avg/stddev):' in line:
                sub_line = line.replace('events (avg/stddev):', '').strip().split('/')
                output['threads_fairness']['events_avg'] = float(sub_line[0])
                output['threads_fairness']['events_stddev'] = float(sub_line[1])
            elif 'execution time (avg/stddev):' in line:
                sub_line = line.replace('execution time (avg/stddev):', '').strip().split('/')
                output['threads_fairness']['execution_time_avg'] = float(sub_line[0])
                output['threads_fairness']['execution_time_stddev'] = float(sub_line[1])
    return output


def load_private_key(name: str) -> str:
    if not os.path.isfile(f'/keypairs/{name}.json'):
        return None
    keypair = None
    with open(f'/keypairs/{name}.json', 'r') as file:
        keypair = json.load(file)
    return paramiko.RSAKey.from_private_key(io.StringIO(keypair['KeyMaterial']))

def is_valid_query(query: str) -> bool:
    try:
        sqlparse.parse(query)
        return True
    except:
        return False

def is_write_query(query: str) -> bool:
    parsed_queries = sqlparse.parse(query)
    for parsed_query in parsed_queries:
        if parsed_query.get_type() in ('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TRUNCATE'):
            return True
    return False
