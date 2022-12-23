from flask import Blueprint, request
import logging, consts, utils, requests




# --------------------------------------------------------------------------- #
# INIT                                                                        #
# --------------------------------------------------------------------------- #

logging.info( '------------ Private hostnames ------------')
logging.info(f'Proxy hostname:  {consts.PROXY_HOSTNAME}')
gtkpr_bp = Blueprint('proxy', __name__)





# --------------------------------------------------------------------------- #
# ROUTES                                                                      #
# --------------------------------------------------------------------------- #

@gtkpr_bp.route("/benchmark/<path:path>", methods=["GET"])
def benchmark(path: str) -> tuple[str, int]:
    '''
    The /benchmark/<path> route implementation.

    This redirect benchmark requests to the proxy without any change.

        Parameters:
            path (str): The benchmark type (standalone/cluster)
    '''

    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/benchmark/{path}', timeout=380)
    return resp.content, resp.status_code





@gtkpr_bp.route("/start", methods=["GET"])
def start() -> tuple[str, int]:
    '''
    The /start route implementation.

    This redirect cluster start requests to the proxy without any change.
    '''

    resp = requests.get(f'http://{consts.PROXY_HOSTNAME}/start', timeout=380)
    return resp.content, resp.status_code





@gtkpr_bp.route("/direct", methods=["POST"])
def direct_proxy():
    '''
    The /direct route implementation.

    This validate and sanitize direct query requests before redirecting them
    to the proxy instance.
    '''

    # Fetch the query from the request
    data = request.get_json()
    query: str = data.get('query')

    # Verify if the query is valid
    if query is None:
        return 'Missing query.', 400
    elif not isinstance(query, str) or not utils.is_valid_query(query):
        return 'Invalid query.', 400
    
    # Redirect the request to the proxy
    resp = requests.post(f'http://{consts.PROXY_HOSTNAME}/direct', json={'query': query}, timeout=120)
    return resp.content, resp.status_code





@gtkpr_bp.route("/random", methods=["POST"])
def random_proxy():
    '''
    The /random route implementation.

    This validate and sanitize random query requests before redirecting them
    to the proxy instance.

    It will refuse any invalid and or writing queries.
    '''

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
    resp = requests.post(f'http://{consts.PROXY_HOSTNAME}/random', json={'query': query}, timeout=120)
    return resp.content, resp.status_code
    




@gtkpr_bp.route("/custom", methods=["POST"])
def custom_proxy():
    '''
    The /custom route implementation.

    This validate and sanitize custom query requests before redirecting them
    to the proxy instance.

    It will refuse any invalid queries and will redirect writing requests to
    to the direct mode (master node only).
    '''

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
        resp = requests.post(f'http://{consts.PROXY_HOSTNAME}/direct', json={'query': query}, timeout=120)
    
    # Read queries will be redirected to the /custom path of the proxy
    else:
        resp = requests.post(f'http://{consts.PROXY_HOSTNAME}/custom', json={'query': query}, timeout=120)

    return resp.content, resp.status_code