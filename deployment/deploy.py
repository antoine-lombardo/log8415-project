
import boto3
import logging
from boto3_type_annotations.ec2 import ServiceResource as ec2ServiceResource
from boto3_type_annotations.ec2 import Client as ec2Client
from boto3_type_annotations.ec2 import Instance as ec2Instance
import aws.security_groups, aws.instances

# Constants
SECURITY_GROUP_NAME = 'tp1'
MASTER_INSTANCE = {}
INSTANCE_INFOS = {
    'standalone':
    {
        'names': ['2018968-standalone'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'standalone/instance-setup/setup.sh'
    },
    'master':
    {
        'names': ['2018968-master'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'cluster/instance-setup/master.sh'
    },
    'slaves':
    {
        'names': ['2018968-slave1', '2018968-slave2', '2018968-slave3'],
        'type': 't2.micro', 
        'zone': 'us-east-1a', 
        'image_id': 'ami-0574da719dca65348',
        'script': 'cluster/instance-setup/slave.sh'
    }
}

def deploy() -> ec2Instance:
    '''
    Fully deploy a ec2 instance with all scripts installed.
    '''

    ec2_service_resource: ec2ServiceResource = boto3.resource('ec2')
    ec2_client: ec2Client = boto3.client('ec2')

    # Delete all old objects
    #aws.instances.delete_all_instances(ec2_service_resource)

    # Create/edit the security group
    security_group = aws.security_groups.get_security_group(ec2_service_resource, 'default')
    aws.security_groups.add_ssh_rules(security_group)

    # Create the Master instance
    master_instance = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['master'],
        security_group
    )[0]
    aws.instances.wait_for_initialized(ec2_client, master_instance)

    # Create Slaves instances
    slaves_instances = aws.instances.create_instances(
        ec2_service_resource,
        ec2_client,
        INSTANCE_INFOS['slaves'],
        security_group,
        [master_instance.private_dns_name]
    )
    for slave_instance in slaves_instances:
        aws.instances.wait_for_initialized(ec2_client, slave_instance)

    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    deploy()