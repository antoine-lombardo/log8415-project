from app import app, SLAVES, PUBLIC_MASTER_HOSTNAME, PUBLIC_STANDALONE_HOSTNAME, MASTER_HOSTNAME
from flask import redirect

app.logger.info( '------------ Private hostnames ------------')
app.logger.info(f'Master hostname:  {MASTER_HOSTNAME}')
app.logger.info(f'Slave 1 hostname: {SLAVES[0]}')
app.logger.info(f'Slave 2 hostname: {SLAVES[1]}')
app.logger.info(f'Slave 3 hostname: {SLAVES[2]}')

app.logger.info( '------------ Public hostnames ------------')
app.logger.info(f'Stdaln hostname: {PUBLIC_STANDALONE_HOSTNAME}')
app.logger.info(f'Master hostname: {PUBLIC_MASTER_HOSTNAME}')

@app.route("/benchmark/cluster", methods=["GET"])
def cluster_benchmark():
    """

    Redirect to the benchmark of the master node.

    """

    return redirect(f'http://{PUBLIC_MASTER_HOSTNAME}/benchmark', code=302)


@app.route("/benchmark/standalone", methods=["GET"])
def standalone_benchmark():
    """

    Redirect to the benchmark of the master node.

    """

    return redirect(f'http://{PUBLIC_STANDALONE_HOSTNAME}/benchmark', code=302)