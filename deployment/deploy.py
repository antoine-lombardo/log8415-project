
import boto3
import logging
import requests
import time
from boto3_type_annotations.ec2 import ServiceResource as ec2ServiceResource
from boto3_type_annotations.ec2 import Client as ec2Client
from boto3_type_annotations.ec2 import Instance as ec2Instance
import aws.security_groups, aws.instances, aws.keypairs

# Constants
SECURITY_GROUP_NAME = 'tp1'
MASTER_INSTANCE = {}
INSTANCE_INFOS = {
    'standalone':
    {
        'names': ['io-stdaln'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'standalone/instance-setup/setup.sh'
    },
    'master':
    {
        'names': ['io-master'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'cluster/instance-setup/master.sh'
    },
    'slaves':
    {
        'names': ['io-slave1', 'io-slave2', 'io-slave3'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'cluster/instance-setup/slave.sh'
    },
    'proxy':
    {
        'names': ['io-proxy'],
        'type': 't2.large', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'proxy/instance-setup/setup.sh'
    }
}

def deploy() -> ec2Instance:
    '''
    Fully deploy a ec2 instance with all scripts installed.
    '''

    ec2_service_resource: ec2ServiceResource = boto3.resource('ec2')
    ec2_client: ec2Client = boto3.client('ec2')

    # Delete all old objects
    aws.instances.delete_all_instances(ec2_service_resource)

    # Create/edit the security group
    master_security_group     = aws.security_groups.create_security_group(ec2_service_resource, 'sgo-master')
    slaves_security_group     = aws.security_groups.create_security_group(ec2_service_resource, 'sgo-slaves')
    proxy_security_group      = aws.security_groups.create_security_group(ec2_service_resource, 'sgo-proxy' )
    standalone_security_group = aws.security_groups.create_security_group(ec2_service_resource, 'sgo-stdaln')

    # Allow SSH from anywhere
    aws.security_groups.add_ssh_rule(master_security_group    )
    aws.security_groups.add_ssh_rule(slaves_security_group    )
    aws.security_groups.add_ssh_rule(proxy_security_group     )
    aws.security_groups.add_ssh_rule(standalone_security_group)

    # Allow HTTP and HTTPS to master and standalone
    aws.security_groups.add_http_rule(master_security_group    )
    aws.security_groups.add_http_rule(proxy_security_group     )
    aws.security_groups.add_http_rule(standalone_security_group)

    # Allow packets from the same security group
    aws.security_groups.add_sg_rule(slaves_security_group    , slaves_security_group    )
    aws.security_groups.add_sg_rule(master_security_group    , master_security_group    )
    aws.security_groups.add_sg_rule(proxy_security_group     , proxy_security_group     )
    aws.security_groups.add_sg_rule(standalone_security_group, standalone_security_group)

    # Allow packets from the proxy to master and slaves
    aws.security_groups.add_sg_rule(master_security_group, proxy_security_group)
    aws.security_groups.add_sg_rule(slaves_security_group, proxy_security_group)

    # Allow packets from the master to slaves and from slaves to master
    aws.security_groups.add_sg_rule(slaves_security_group, master_security_group)
    aws.security_groups.add_sg_rule(master_security_group, slaves_security_group)

    # Create a keypair
    keypair = aws.keypairs.initialize_keypair(ec2_client, ec2_service_resource, 'kp-main')

    # Create the standalone instance
    stdaln_instance = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['standalone'],
        standalone_security_group,
        keypair
    )[0]

    # Create Slaves instances (must be created before the Master)
    slaves_instances = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['slaves'],
        slaves_security_group,
        keypair
    )

    # Create the Master instance
    slave_hostnames = []
    for slave_instance in slaves_instances:
        slave_hostnames.append(slave_instance.private_dns_name)
    master_instance = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['master'],
        master_security_group,
        keypair,
        slave_hostnames
    )[0]

    # Create the Proxy instance
    cluster_hostnames = slave_hostnames
    cluster_hostnames.append(master_instance.private_dns_name)
    cluster_hostnames.append(master_instance.public_dns_name)
    cluster_hostnames.append(stdaln_instance.public_dns_name)
    proxy_instance = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['proxy'],
        proxy_security_group,
        keypair,
        cluster_hostnames
    )[0]

    # Wait for initializations
    aws.instances.wait_for_initialized(ec2_client, master_instance)
    for slave_instance in slaves_instances:
        aws.instances.wait_for_initialized(ec2_client, slave_instance)
    aws.instances.wait_for_initialized(ec2_client, stdaln_instance)
    aws.instances.wait_for_initialized(ec2_client, proxy_instance)

    


def start():
    ec2_service_resource: ec2ServiceResource = boto3.resource('ec2')
    ec2_client: ec2Client = boto3.client('ec2')

    # Retrieve the instances
    master = aws.instances.retrieve_instance(ec2_service_resource, INSTANCE_INFOS['master']['names'][0])
    proxy  = aws.instances.retrieve_instance(ec2_service_resource, INSTANCE_INFOS['proxy']['names'][0])

    # Run the cluster
    logging.info('Starting the cluster...')
    for attempt in range(5):
        try:
            response = requests.get('http://{}/start'.format(master.public_dns_name), timeout=120)
        except:
            attempt += 1
            if attempt == 5:
                logging.error('Master unreachable.')
                return
            time.sleep(5)
    if response.status_code != 200:
        logging.error('Unable to start the cluster.')
        logging.error(response.text)
        return
    logging.info('  Started.')

    # Initialize the proxy
    logging.info('Initializing the proxy...')
    for attempt in range(5):
        try:
            response = requests.get('http://{}/init'.format(proxy.public_dns_name), timeout=120)
        except:
            attempt += 1
            if attempt == 5:
                logging.error('Proxy unreachable.')
                return
            time.sleep(5)
    if response.status_code != 200:
        logging.error('Unable to initialize the proxy.')
        logging.error(response.text)
        return
    logging.info('  Initilialized.')



    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    deploy()
    start()