from typing import List
from flask import redirect, Blueprint, request
import logging, consts, pymysql, random, utils, pythonping, pymysql.cursors
from sshtunnel import open_tunnel

logging.info( '------------ Private hostnames ------------')
logging.info(f'Master hostname:  {consts.MASTER_HOSTNAME}')
logging.info(f'Slave 1 hostname: {consts.SLAVES[0]}')
logging.info(f'Slave 2 hostname: {consts.SLAVES[1]}')
logging.info(f'Slave 3 hostname: {consts.SLAVES[2]}')

logging.info( '------------ Public hostnames ------------')
logging.info(f'Stdaln hostname: {consts.PUBLIC_STANDALONE_HOSTNAME}')
logging.info(f'Master hostname: {consts.PUBLIC_MASTER_HOSTNAME}')

PRIVATE_KEY = utils.load_private_key('kp-main')

proxy_bp = Blueprint('proxy', __name__)


@proxy_bp.route("/benchmark/cluster", methods=["GET"])
def cluster_benchmark():
    """

    Redirect to the benchmark of the master node.

    """

    return redirect(f'http://{consts.PUBLIC_MASTER_HOSTNAME}/benchmark', code=302)


@proxy_bp.route("/benchmark/standalone", methods=["GET"])
def standalone_benchmark():
    """

    Redirect to the benchmark of the master node.

    """

    return redirect(f'http://{consts.PUBLIC_STANDALONE_HOSTNAME}/benchmark', code=302)


@proxy_bp.route("/direct", methods=["POST"])
def direct_proxy():
    """

    Send the query to the master node.

    """

    data = request.get_json()
    query: str = data['query']
    args: List[str] = data.get('args', [])
    output, dbname = make_query(query, args, 'direct')
    return {
        'output': output,
        'node': dbname
    }, 200


@proxy_bp.route("/random", methods=["POST"])
def random_proxy():
    """

    Send the query to a random node.

    """

    data = request.get_json()
    query: str = data['query']
    args: List[str] = data.get('args', [])
    output, dbname = make_query(query, args, 'random')
    return {
        'output': output,
        'node': dbname
    }, 200
    


@proxy_bp.route("/custom", methods=["POST"])
def custom_proxy():
    """

    Send the query to the node with the lowest latency.

    """

    data = request.get_json()
    query: str = data['query']
    args: List[str] = data.get('args', [])
    output, dbname = make_query(query, args, 'custom')
    return {
        'output': output,
        'node': dbname
    }, 200


def get_bd(mode: str) -> str:
    if mode == 'direct':
        return consts.MASTER_HOSTNAME, 'master'
    elif mode == 'random':
        i = random.randint(0, 2)
        return consts.SLAVES[i], 'slave' + str(i+1)
    elif mode == 'custom':
        db = {
            'hostname': consts.MASTER_HOSTNAME,
            'name': 'master',
            'latency': pythonping.ping(target=consts.MASTER_HOSTNAME, count=1, timeout=10).rtt_avg
        }
        for i in range(len(consts.SLAVES)):
            latency = pythonping.ping(target=consts.SLAVES[i], count=1, timeout=10).rtt_avg
            if latency < db['latency']:
                db = {
                    'hostname': consts.SLAVES[i],
                    'name': 'slave' + str(i+1),
                    'latency': latency
                }
        return db['hostname'], db['name']
    else:
        return None

def make_query(query:str, args: List, mode: str) -> str:
    db, name = get_bd(mode)
    if db is None:
        return None
    with open_tunnel(
      (db, 22),
      ssh_username='ubuntu',
      ssh_pkey=PRIVATE_KEY,
      remote_bind_address=(consts.MASTER_HOSTNAME, 3306),
      local_bind_address=('0.0.0.0', 3306)) as tunnel:
        with pymysql.connect(
          host='localhost', 
          user='myapp', 
          password='testpwd', 
          port=330,
          charset='utf8mb4',
          cursorclass=pymysql.cursors.DictCursor) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchone(), name
    