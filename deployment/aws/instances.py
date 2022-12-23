import os, logging, time, json
from typing import Any, Dict, List
from boto3_type_annotations.ec2 import ServiceResource, SecurityGroup, Instance, Client





# Read the user_data file
USER_DATA_SCRIPT_FILE = 'instance_user_data.txt'
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, USER_DATA_SCRIPT_FILE)) as file:
    USER_DATA_SCRIPT = file.read()





def delete_all_instances(ec2: ServiceResource):
    '''

    Deletes all running instances
    
        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
    '''

    logging.info('Terminating old instances...')
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            instance.terminate()
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            #instance.wait_until_terminated()
            logging.info('  {}: Terminated.'.format(instance.id))





def create_instances(
    ec2:                ServiceResource,
    instances_infos:    Dict[str, Any], 
    security_group:     SecurityGroup, 
    keypair:            Dict, 
    setup_args:         List[str] = []
    ) -> List[Instance]:
    '''
    Creates EC2 instances

        Parameters:
            ec2 (ServiceResource):          The EC2 service resource object
            instances_infos (Dict):         The instances infos
            security_group (SecurityGroup): The security group to be applied to the instance
            keypair (Dict):                 The keypair to be used for authenticating to the instances
            setup_args (List[str]):         A list of arguments to pass to the setup script
        
        Returns:
            instance (List[Instance]): A list of all the created instances.
    '''

    # Retrieve the instances parameters
    type     = instances_infos['type']
    zone     = instances_infos['zone']
    image_id = instances_infos['image_id']
    script   = instances_infos['script']
    names    = instances_infos['names']
    n = len(names)
    
    # Print a task header
    if n == 1:
        logging.info(f'Creating instance "{names[0]}" of type "{type}" instance in zone "{zone}"...')
    else:
        logging.info(f'Creating {n} instances of type "{type}" instance in zone "{zone}"...')
    
    # Generate a bash command to copy the keypair to the instance
    raw_keypair = json.dumps(keypair).replace('"', '\\"')
    keypair_cmd = f'echo "{raw_keypair}" > /keypairs/{keypair["KeyName"]}.json'

    # Fill the user data script
    form_user_data_script = USER_DATA_SCRIPT.format(
        instance_setup_script=script, 
        instance_setup_args=' '.join(setup_args), 
        keypair_cmd=keypair_cmd)
    
    # Create the instances
    instances: Instance = ec2.create_instances(
        ImageId=image_id,
        MinCount=n,
        MaxCount=n,
        InstanceType=type,
        UserData=form_user_data_script,
        KeyName=keypair['KeyName'],
        Placement={
            'AvailabilityZone': zone,
        },
        SecurityGroupIds=[security_group.id]
    )
    time.sleep(1)

    # Print a created message
    for i in range(n):
        logging.info('  {}: Created.'.format(names[i]))
    
    # Name each instance
    for i in range(n):
        logging.info('  {}: Naming...'.format(names[i]))
        ec2.create_tags(
            Resources=[instances[i].id], 
            Tags=[{'Key': 'Name', 'Value': names[i]}])
        logging.info('  {}: Named.'.format(names[i]))
    
    # Wait for all instances to be running
    # (This step is necessary to get the DNSs)
    for i in range(n):
        logging.info('  {}: Starting...'.format(names[i]))
        wait_for_running(instances[i])
        instances[i].load()
        logging.info('  {}: Started.'.format(names[i]))

    # Print the DNS names of each instances
    for i in range(n):
        logging.info('  {}: Public DNS.: {}'.format(names[i], instances[i].public_dns_name))
        logging.info('  {}: Private DNS: {}'.format(names[i], instances[i].private_dns_name))

    return instances





def wait_for_running(instance: Instance):
    '''
    Waits for an instance to be running.

        Parameters:
            instance (Instance): The instance to wait for
    '''

    instance.wait_until_running()





def wait_for_initialized(client: Client, instance: Instance):
    '''
    Waits for an instance to be initialized.

        Parameters:
            client (Client):     The EC2 client object
            instance (Instance): The instance to wait for
    '''

    # Try to get the instance name, fallback to the id
    name = instance.id
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            name = tag['Value']
            break

    # Print a header for the task
    logging.info('  {}: Waiting for initialization...'.format(name))

    # Wait for system status ok
    system_status_ok_waiter = client.get_waiter('system_status_ok')
    system_status_ok_waiter.wait(
        InstanceIds=[instance.id], 
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 60
        })
    
    # Wait for instance status ok
    instance_status_ok_waiter = client.get_waiter('instance_status_ok')
    instance_status_ok_waiter.wait(
        InstanceIds=[instance.id],
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 60
        })
    
    # Post-completion
    instance.load()
    logging.info('  {}: Initialized.'.format(name))





def retrieve_instances(ec2: ServiceResource) -> List[Instance]:
    '''
    Retrieves all running instances.

        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
        
        Returns:
            instances (List[Instance]): All the running instances
    '''

    instances = []
    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            instances.append(instance)
    return instances





def retrieve_instance(ec2: ServiceResource, name: str) -> Instance:
    '''
    Retrieve the instance with the name provided.

        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
        
        Returns:
            instance (Instance): The matching instance, or None
    '''

    for instance in ec2.instances.all():
        if instance.state['Name'] != 'terminated':
            for tag in instance.tags:
                if tag['Key'] == 'Name' and tag['Value'] == name:
                    return instance
    return None