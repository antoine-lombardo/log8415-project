import logging, utils, consts
from flask import Flask, request


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S')


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
app.logger.info(f'App started in mode: {consts.APP_MODE}')


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

if consts.APP_MODE == 'MASTER':
    from routes.master import master_bp
    app.register_blueprint(master_bp)

elif consts.APP_MODE == 'SLAVE':
    from routes.slave import slave_bp
    app.register_blueprint(slave_bp)

elif consts.APP_MODE == 'STANDALONE':
    from routes.standalone import standalone_bp
    app.register_blueprint(standalone_bp)

elif consts.APP_MODE == 'PROXY':
    from routes.proxy import proxy_bp
    app.register_blueprint(proxy_bp)


# Start in production mode
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)