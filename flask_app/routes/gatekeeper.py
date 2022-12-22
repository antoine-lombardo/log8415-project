from typing import List
from flask import redirect, Blueprint, request
import logging, consts, pymysql, random, utils, pythonping, pymysql.cursors, requests
from sshtunnel import open_tunnel

logging.info( '------------ Private hostnames ------------')
logging.info(f'Proxy hostname:  {consts.PROXY_HOSTNAME}')

gtkpr_bp = Blueprint('proxy', __name__)


@gtkpr_bp.route("/benchmark/<path:path>", methods=["GET"])
def benchmark(path: str):
    """

    Redirect benchmarks requests to proxy without any change.

    """

    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/benchmark/{path}', timeout=380)
    return resp.content, resp.status_code


@gtkpr_bp.route("/start", methods=["GET"])
def start():
    """

    Redirect benchmarks requests to proxy without any change.

    """

    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/start', timeout=380)
    return resp.content, resp.status_code


@gtkpr_bp.route("/direct", methods=["POST"])
def direct_gatekeeper():
    """

    Validate then redirect queries to the proxy.

    """

    # Fetch the query from the request
    data = request.get_json()
    query: str = data.get('query')

    # Verify if the query is valid
    if query is None:
        return 'Missing query.', 400
    elif not isinstance(query, str) or not utils.is_valid_query(query):
        return 'Invalid query.', 400
    
    # Redirect the request to the proxy
    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/direct', json={'query': query}, timeout=120)
    return resp.content, resp.status_code


@gtkpr_bp.route("/random", methods=["POST"])
def random_proxy():
    """

    Validate then redirect queries to the proxy.

    """

    # Fetch the query from the request
    data = request.get_json()
    query: str = data.get('query')

    # Verify if the query is valid
    if query is None:
        return 'Missing query.', 400
    elif not isinstance(query, str) or not utils.is_valid_query(query):
        return 'Invalid query.', 400

    # Verify if the query is a write query
    elif utils.is_write_query(query):
        return 'This query perform write operations, it cannot be served by a slave node.', 400
    
    # Redirect the request to the proxy
    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/random', json={'query': query}, timeout=120)
    return resp.content, resp.status_code
    


@gtkpr_bp.route("/custom", methods=["POST"])
def custom_proxy():
    """

    Validate then redirect queries to the proxy.

    """

    # Fetch the query from the request
    data = request.get_json()
    query: str = data.get('query')

    # Verify if the query is valid
    if query is None:
        return 'Missing query.', 400
    elif not isinstance(query, str) or not utils.is_valid_query(query):
        return 'Invalid query.', 400

    # Write queries will be redirected to the /direct path of the proxy
    elif utils.is_write_query(query):
        resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/direct', json={'query': query}, timeout=120)
    
    # Read queries will be redirected to the /custom path of the proxy
    else:
        resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/custom', json={'query': query}, timeout=120)

    return resp.content, resp.status_code