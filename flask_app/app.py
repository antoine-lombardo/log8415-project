import os, logging, requests, utils, subprocess, time
from flask import Flask, request




logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S')


# --------------------------------------------------------------------------- #
# GLOBALS                                                                     #
# --------------------------------------------------------------------------- #

SLAVES = [
    os.environ.get('SLAVE1_HOSTNAME'),
    os.environ.get('SLAVE2_HOSTNAME'),
    os.environ.get('SLAVE3_HOSTNAME'),
]
APP_MODE = os.environ.get('APP_MODE')
HOSTNAME = subprocess.run(['hostname', '-f'], stdout=subprocess.PIPE).stdout.decode('utf-8')



# --------------------------------------------------------------------------- #
# INIT                                                                        #
# --------------------------------------------------------------------------- #

# Configure the Flask app
app = Flask('log8415-project')
app.logger.setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('waitress').setLevel(logging.INFO)


# --------------------------------------------------------------------------- #
# OUTPUT SESSION INFOS                                                        #
# --------------------------------------------------------------------------- #
app.logger.info(f'App started in mode: {APP_MODE}')
if APP_MODE == 'MASTER':
    app.logger.info(f'Slave 1 hostname: {SLAVES[0]}')
    app.logger.info(f'Slave 2 hostname: {SLAVES[1]}')
    app.logger.info(f'Slave 3 hostname: {SLAVES[2]}')


# --------------------------------------------------------------------------- #
# UTILS                                                                       #
# --------------------------------------------------------------------------- #

@app.after_request
def log_the_request(response):
    app.logger.info('{} - {} - {}'.format(utils.client_ip().center(15), response.status_code, request.path))
    return response





# --------------------------------------------------------------------------- #
# MASTER MODE ROUTES                                                          #
# --------------------------------------------------------------------------- #

@app.route("/slaves/<int:slave_id>/start", methods=["GET"])
def remote_slave_start(slave_id: int) -> tuple[str, int]:
    """

    Remotely starts a slave node.

    """

    if APP_MODE != 'MASTER':
        return 'This request should be sent to the Master node.', 404

    if slave_id < 0 or slave_id >= len(SLAVES):
        return 'Invalid Slave ID.', 400

    resp = requests.get(
        url=f'http://{SLAVES[slave_id]}/start/{HOSTNAME}',
        timeout=60
    )

    return resp.content, resp.status_code



@app.route("/start", methods=["GET"])
def master_start() -> tuple[str, int]:
    """

    Starts the Master node.

    """

    if APP_MODE != 'MASTER':
        return 'This request should be sent to the Master node.', 404

    # Check the current status
    status = utils.get_cluster_status()

    # If mgmd is not running, return an error
    if not status['manager']:
        return 'mgmd is not running.', 500

    # Ensure slaves are running
    err = utils.ensure_slaves_are_up(SLAVES, HOSTNAME)
    if err:
        return err, 500
    
    # Ensure mysqld is running
    err = utils.ensure_mysqld_is_up(app)
    if err:
        return err, 500
    
    # No error, everything seems to be running
    return utils.get_cluster_status(), 200



@app.route("/benchmark", methods=["GET"])
def master_benchmark() -> tuple[str, int]:
    """

    Starts the Master node.

    """

    if APP_MODE != 'MASTER':
        return 'This request should be sent to the Master node.', 404

    # Check the current status
    status = utils.get_cluster_status()

    if not status['manager'] or \
       not status['mysqld'] or \
       len(status['slaves']) < len(SLAVES) or \
       not all(status['slaves']):
        return 'Cluster is not ready to start a benchmark.', 500

    app.logger.info('Preparing benchmark...')
    subprocess.run(['/scripts/cluster/benchmark/prepare_db.sh'], stdout=subprocess.PIPE, timeout=15)
    time.sleep(2)
    app.logger.info('Running benchmark...')
    return subprocess.run(['/scripts/cluster/benchmark/run.sh'], stdout=subprocess.PIPE, timeout=60).stdout.decode('utf-8'), 200




# --------------------------------------------------------------------------- #
# SLAVE MODE ROUTES                                                           #
# --------------------------------------------------------------------------- #

@app.route("/start/<string:master_hostname>", methods=["GET"])
def slave_start(master_hostname: str) -> tuple[str, int]:
    """

    Starts the current slave node.

    """

    if APP_MODE != 'SLAVE':
        return 'This request should be sent to a Slave node.', 404

    subprocess.run(['killall', 'ndbd'], stdout=subprocess.PIPE)
    time.sleep(1)
    output = subprocess.run(['/scripts/cluster/setup/slave/start_ndbd.sh', master_hostname], stdout=subprocess.PIPE, timeout=10).stdout.decode('utf-8')
    response = {
        'connected': False,
        'node_id': -1,
        'timed_out': True
    }
    for line in output.split('\n'):
        if 'Angel connected to' in line:
            response['connected'] = True
            response['timed_out'] = False
        elif 'Angel allocated nodeid: ' in line:
            response['node_id'] = int(line[line.index('Angel allocated nodeid: ') + 24:].strip())
            response['timed_out'] = False
    
    if response['timed_out']:
        return response, 500
    else:
        return response, 200




# Start in production mode
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)