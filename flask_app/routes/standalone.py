from flask import Blueprint
import subprocess, time, utils, logging





# --------------------------------------------------------------------------- #
# INIT                                                                        #
# --------------------------------------------------------------------------- #

standalone_bp = Blueprint('standalone', __name__)





# --------------------------------------------------------------------------- #
# ROUTES                                                                      #
# --------------------------------------------------------------------------- #

@standalone_bp.route("/benchmark", methods=["GET"])
def benchmark() -> tuple[str, int]:
    '''
    The /benchmark route implementation.

    Runs the benchmark and returns the parsed results of it.
    '''

    # Clean the database
    logging.info('Cleaning the database...')
    subprocess.run(['/scripts/standalone/benchmark/clean_db.sh'], stdout=subprocess.PIPE, timeout=30)
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
    return utils.parse_benchmark(lines), 200