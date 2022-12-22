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
MASTER_HOSTNAME = os.environ.get('MASTER_HOSTNAME')
PUBLIC_MASTER_HOSTNAME     = os.environ.get('PUBLIC_MASTER_HOSTNAME')
PUBLIC_STANDALONE_HOSTNAME = os.environ.get('PUBLIC_STANDALONE_HOSTNAME')

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


# --------------------------------------------------------------------------- #
# UTILS                                                                       #
# --------------------------------------------------------------------------- #

@app.after_request
def log_the_request(response):
    app.logger.info('{} - {} - {}'.format(utils.client_ip().center(15), response.status_code, request.path))
    return response


# --------------------------------------------------------------------------- #
# COMMON ROUTES                                                               #
# --------------------------------------------------------------------------- #

@app.route("/ping", methods=["GET"])
def PING() -> tuple[str, int]:
    """

    Ping... Pong!

    """
    return 'pong!', 200


# --------------------------------------------------------------------------- #
# SPECIFIC ROUTES                                                             #
# --------------------------------------------------------------------------- #

if APP_MODE == 'MASTER':
    import routes.master

elif APP_MODE == 'SLAVE':
    import routes.slave

elif APP_MODE == 'STANDALONE':
    import routes.standalone

elif APP_MODE == 'PROXY':
    import routes.proxy


# Start in production mode
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)