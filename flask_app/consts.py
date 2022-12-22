import os, subprocess

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