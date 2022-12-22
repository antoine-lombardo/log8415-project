from app import app, SLAVES
import subprocess, time, utils

@app.route("/benchmark", methods=["GET"])
def benchmark() -> tuple[str, int]:

    # Clean the database
    app.logger.info('Cleaning the database...')
    subprocess.run(['/scripts/standalone/benchmark/clean_db.sh'], stdout=subprocess.PIPE, timeout=30)
    time.sleep(2)

    # Run the benchmark
    app.logger.info('Running benchmark...')
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