import os, logging, requests, utils, subprocess
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

    output = subprocess.run(['/scripts/cluster/start/slave.sh', master_hostname], stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    return output, 200




# Start in production mode
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)