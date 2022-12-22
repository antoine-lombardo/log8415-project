from flask import redirect, Blueprint, request
import logging, consts, pymysql, random, utils
from pymysql import Connection

logging.info( '------------ Private hostnames ------------')
logging.info(f'Master hostname:  {consts.MASTER_HOSTNAME}')
logging.info(f'Slave 1 hostname: {consts.SLAVES[0]}')
logging.info(f'Slave 2 hostname: {consts.SLAVES[1]}')
logging.info(f'Slave 3 hostname: {consts.SLAVES[2]}')

logging.info( '------------ Public hostnames ------------')
logging.info(f'Stdaln hostname: {consts.PUBLIC_STANDALONE_HOSTNAME}')
logging.info(f'Master hostname: {consts.PUBLIC_MASTER_HOSTNAME}')

MASTER_CONN: Connection = None
SLAVE1_CONN: Connection = None
SLAVE2_CONN: Connection = None
SLAVE3_CONN: Connection = None

logging.info( '------------ MySQL Connections ------------')


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


@proxy_bp.route("/init", methods=["GET"])
def init():
    """

    Initializes connections.

    """

    global MASTER_CONN, SLAVE1_CONN, SLAVE2_CONN, SLAVE3_CONN
    if MASTER_CONN is None:
        MASTER_CONN = pymysql.connect(consts.MASTER_HOSTNAME, 'myapp', 'testpwd', 'sakila')
    if SLAVE1_CONN is None:
        SLAVE1_CONN = pymysql.connect(consts.SLAVES[0],       'myapp', 'testpwd', 'sakila')
    if SLAVE2_CONN is None:
        SLAVE2_CONN = pymysql.connect(consts.SLAVES[1],       'myapp', 'testpwd', 'sakila')
    if SLAVE3_CONN is None:
        SLAVE3_CONN = pymysql.connect(consts.SLAVES[2],       'myapp', 'testpwd', 'sakila')

    return 'Connection initialized.', 200


@proxy_bp.route("/direct", methods=["POST"])
def direct():
    """

    Send the query to the master node.

    """

    with MASTER_CONN.cursor() as cursor:
        query: str = request.json()['query']
        cursor.execute(query)
        return {
            'node': 'master',
            'output': cursor.fetchone()
        }, 200


@proxy_bp.route("/random", methods=["POST"])
def random():
    """

    Send the query to a random node.

    """

    i = random.randint(1, 3)
    conn = None
    if i == 1:
        conn = SLAVE1_CONN
    elif i == 2:
        conn = SLAVE2_CONN
    else:
        conn = SLAVE3_CONN

    with conn.cursor() as cursor:
        query: str = request.json()['query']
        cursor.execute(query)
        return {
            'node': 'slave' + str(i),
            'output': cursor.fetchone()
        }, 200


@proxy_bp.route("/custom", methods=["POST"])
def random():
    """

    Send the query to the node with the lowest latency.

    """

    conns = []
    conns.append({'conn': MASTER_CONN, 'hostname': consts.MASTER_HOSTNAME, 'name': 'master'})
    conns.append({'conn': SLAVE1_CONN, 'hostname': consts.SLAVES[0], 'name': 'slave1'})
    conns.append({'conn': SLAVE2_CONN, 'hostname': consts.SLAVES[1], 'name': 'slave2'})
    conns.append({'conn': SLAVE3_CONN, 'hostname': consts.SLAVES[2], 'name': 'slave3'})

    fastest_conn = None
    for conn in conns:
        conn['ping'] = utils.ping(conn['hostname'])
        if fastest_conn is None or fastest_conn['ping'] > conn['ping']:
            fastest_conn = conn

    with fastest_conn['conn'].cursor() as cursor:
        query: str = request.json()['query']
        cursor.execute(query)
        return {
            'node': fastest_conn['name'],
            'output': cursor.fetchone()
        }, 200