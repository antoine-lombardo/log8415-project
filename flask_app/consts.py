import os, subprocess



# This constants will be used the gatekeeper, the proxy and the master

SLAVES = [  os.environ.get('SLAVE1_HOSTNAME'),
            os.environ.get('SLAVE2_HOSTNAME'),
            os.environ.get('SLAVE3_HOSTNAME')  ]
MASTER_HOSTNAME         = os.environ.get('MASTER_HOSTNAME')
PROXY_HOSTNAME          = os.environ.get('PROXY_HOSTNAME')
PUBLIC_MASTER_HOSTNAME  = os.environ.get('PUBLIC_MASTER_HOSTNAME')
STANDALONE_HOSTNAME     = os.environ.get('STANDALONE_HOSTNAME')
APP_MODE                = os.environ.get('APP_MODE')
HOSTNAME                = subprocess.run(['hostname', '-f'], stdout=subprocess.PIPE).stdout.decode('utf-8')