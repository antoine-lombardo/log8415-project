from flask import redirect, Blueprint
import logging, consts

logging.info( '------------ Private hostnames ------------')
logging.info(f'Master hostname:  {consts.MASTER_HOSTNAME}')
logging.info(f'Slave 1 hostname: {consts.SLAVES[0]}')
logging.info(f'Slave 2 hostname: {consts.SLAVES[1]}')
logging.info(f'Slave 3 hostname: {consts.SLAVES[2]}')

logging.info( '------------ Public hostnames ------------')
logging.info(f'Stdaln hostname: {consts.PUBLIC_STANDALONE_HOSTNAME}')
logging.info(f'Master hostname: {consts.PUBLIC_MASTER_HOSTNAME}')


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