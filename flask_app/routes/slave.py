from flask import Blueprint
import subprocess, time

slave_bp = Blueprint('slave', __name__)

@slave_bp.route("/start/<string:master_hostname>", methods=["GET"])
def slave_start(master_hostname: str) -> tuple[str, int]:
    """

    Starts the current slave node.

    """

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