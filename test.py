import sshtunnel, paramiko, json, os, io, pymysql

if not os.path.isfile(f'deployment/keypairs/kp-main.json'):
    os._exit(1)
keypair = None
with open('deployment/keypairs/kp-main.json', 'r') as file:
    keypair = json.load(file)
PKEY_STR = keypair['KeyMaterial']
PKEY = paramiko.RSAKey.from_private_key(io.StringIO(PKEY_STR))



with sshtunnel.open_tunnel(
    ('ec2-3-88-179-252.compute-1.amazonaws.com', 22),
        ssh_username='ubuntu',
        ssh_pkey=PKEY,
        remote_bind_address=('ip-172-31-25-60.ec2.internal', 3306),
        local_bind_address=('0.0.0.0', 3306)
    ):
    conn = pymysql.connect(host='localhost', user='myapp', password='testpwd', port=3306)
    conn.thread_id()
    
