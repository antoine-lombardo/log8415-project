import os, logging
from typing import Dict, List
import boto3
from boto3_type_annotations.ec2 import ServiceResource, SecurityGroup, Instance, waiter, Client

USER_DATA_SCRIPT_FILE = 'instance_user_data.txt'
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, USER_DATA_SCRIPT_FILE)) as file:
    USER_DATA_SCRIPT = file.read()

def delete_all_instances(ec2: ServiceResource):
    logging.info('Terminating old instances...')
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            instance.terminate()
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            instance.wait_until_terminated()
            logging.info('  {}: Terminated.'.format(instance.id))


def create_instances(ec2: ServiceResource, ec2_client: Client, instances_infos: Dict[str, str], security_group: SecurityGroup, setup_args: List[str] = []) -> List[Instance]:
    type     = instances_infos['type']
    zone     = instances_infos['zone']
    image_id = instances_infos['image_id']
    script   = instances_infos['script']
    names    = instances_infos['names']
    n = len(names)
    
    if n == 1:
        logging.info(f'Creating instance "{names[0]}" of type "{type}" instance in zone "{zone}"...')
    else:
        logging.info(f'Creating {n} instances of type "{type}" instance in zone "{zone}"...')
    
    form_user_data_script = USER_DATA_SCRIPT.format(instance_setup_script=script, instance_setup_args=' '.join(setup_args))
    
    instances: Instance = ec2.create_instances(
        ImageId=image_id,
        MinCount=n,
        MaxCount=n,
        InstanceType=type,
        UserData=form_user_data_script,
        KeyName='vockey',
        Placement={
            'AvailabilityZone': zone,
        },
        SecurityGroupIds=[security_group.id]
    )

    for i in range(n):
        logging.info('  {}: Created.'.format(names[i]))
    
    for i in range(n):
        logging.info('  {}: Adding tags...'.format(names[i]))
        ec2.create_tags(
            Resources=[instances[i].id], 
            Tags=[{'Key': 'Name', 'Value': names[i]}])
    
    for i in range(n):
        logging.info('  {}: Starting...'.format(names[i]))
        wait_for_running(instances[i])
        instances[i].load()
        logging.info('  {}: Started.'.format(names[i]))

    for i in range(n):
        logging.info('  {}: Public DNS.: {}'.format(names[i], instances[i].public_dns_name))
        logging.info('  {}: Private DNS: {}'.format(names[i], instances[i].private_dns_name))

    return instances

def wait_for_running(instance: Instance):
    instance.wait_until_running()

def wait_for_initialized(client: Client, instance: Instance):
    logging.info('  {}: Waiting for initialization...'.format(instance.id))
    system_status_ok_waiter = client.get_waiter('system_status_ok')
    system_status_ok_waiter.wait(
        InstanceIds=[instance.id], 
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 60
        })
    instance_status_ok_waiter = client.get_waiter('instance_status_ok')
    instance_status_ok_waiter.wait(
        InstanceIds=[instance.id],
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 60
        })
    instance.load()
    logging.info('  {}: Initialized.'.format(instance.id))

def retrieve_instances(ec2: ServiceResource) -> List[Instance]:
    instances = []
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            instances.append(instance)
    return instances

def retrieve_instance(ec2: ServiceResource, name: str) -> List[Instance]:
    instances = []
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            for tag in instance.tags:
                if tag['Key'] == 'Name' and tag['Value'] == name:
                    return instance
    return None