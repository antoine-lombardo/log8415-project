from flask import Blueprint
import utils, subprocess, time, consts, logging


logging.info( '------------ Private hostnames ------------')
logging.info(f'Slave 1 hostname: {consts.SLAVES[0]}')
logging.info(f'Slave 2 hostname: {consts.SLAVES[1]}')
logging.info(f'Slave 3 hostname: {consts.SLAVES[2]}')


master_bp = Blueprint('master', __name__)
@master_bp.route('/start', methods=["GET"])
def start() -> tuple[str, int]:
    """

    Starts the Master node.

    """

    # Check the current status
    status = utils.get_cluster_status()

    # If mgmd is not running, return an error
    if not status['manager']:
        return 'mgmd is not running.', 500

    # Ensure slaves are running
    err = utils.ensure_slaves_are_up(consts.SLAVES, consts.HOSTNAME)
    if err:
        return err, 500
    
    # Ensure mysqld is running
    err = utils.ensure_mysqld_is_up()
    if err:
        return err, 500
    
    # No error, everything seems to be running
    return utils.get_cluster_status(), 200



@master_bp.route('/benchmark', methods=["GET"])
def benchmark() -> tuple[str, int]:

    # Check the current status
    status = utils.get_cluster_status()
    if not status['manager'] or \
       not status['mysqld'] or \
       len(status['slaves']) < len(consts.SLAVES) or \
       not all(status['slaves']):
        return 'Cluster is not ready to start a benchmark.', 500

    # Clean the database
    logging.info('Cleaning the database...')
    subprocess.run(['/scripts/cluster/benchmark/clean_db.sh'], stdout=subprocess.PIPE, timeout=30)
    time.sleep(2)

    # Run the benchmark
    logging.info('Running benchmark...')
    output = subprocess.run(['/scripts/cluster/benchmark/run.sh'], stdout=subprocess.PIPE, timeout=360).stdout.decode('utf-8')
    
    # Only keep the results section
    lines = output.split('\n')
    start = None
    end = None
    for i in range(len(lines)):
        if 'SQL statistics:' in lines[i]:
            start = i
        elif start is not None and 'sysbench' in lines[i]:
            end = i
            break
    if start is None or end is None:
        return 'Cannot parse the output of the benchmark.', 500
    return '\n'.join(lines[start:end]), 200