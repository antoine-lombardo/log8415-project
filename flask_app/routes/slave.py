from flask import Blueprint
import subprocess, time





# --------------------------------------------------------------------------- #
# INIT                                                                        #
# --------------------------------------------------------------------------- #

slave_bp = Blueprint('slave', __name__)





# --------------------------------------------------------------------------- #
# ROUTES                                                                      #
# --------------------------------------------------------------------------- #

@slave_bp.route("/start/<string:master_hostname>", methods=["GET"])
def slave_start(master_hostname: str) -> tuple[str, int]:
    '''
    The /start/<master_hostname> route implementation.

    This will try to connect the data node to the master node

        Parameters:
            master_hostname (str): The private hostname of the master node
    '''

    # Stop any running ndbd process
    subprocess.run(['killall', 'ndbd'], stdout=subprocess.PIPE)
    time.sleep(1)

    # Try to start ndbd
    output = subprocess.run(['/scripts/cluster/setup/slave/start_ndbd.sh', master_hostname], stdout=subprocess.PIPE, timeout=10).stdout.decode('utf-8')
    
    # Parse the stdout output
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
    
    # Return wether it has connected to the master correctly
    if response['timed_out']:
        return response, 500
    else:
        return response, 200