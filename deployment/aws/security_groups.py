from time import sleep
from typing import Collection
import logging, sys
from boto3_type_annotations.ec2 import ServiceResource, SecurityGroup





def get_security_group(ec2: ServiceResource, name: str) -> SecurityGroup:
    '''
    Returns the security group base on the provided name.
    
        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
            name (str):            The security group name

        Returns:
            security_group (SecurityGroup): The security group
    '''

    security_groups: Collection[SecurityGroup] = ec2.security_groups.all()
    for security_group in security_groups:
        if security_group.group_name == name:
            return security_group
    return None






def delete_security_group(ec2: ServiceResource, name: str):
    '''
    Deletes the security group based on the provided name.
    
        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
            name (str):            The security group name
    '''

    logging.info(f'Deleting security group...')
    security_group = get_security_group(ec2, name)
    for i in range(50):
        security_group.reload()
        try:
            if security_group.ip_permissions:
                security_group.revoke_ingress(IpPermissions=security_group.ip_permissions)
            security_group.delete()
            logging.info(f'  {name}: Deleted.')
            return
        except:
            sleep(2)
    logging.error('Unable to delete the security group. Please relaunch the script.')
    sys.exit(1)





def create_security_group(ec2: ServiceResource, name: str) -> SecurityGroup:
    '''
    Creates a security group.
    
        Parameters:
            ec2 (ServiceResource): The EC2 service resource object
            name (str):            The security group name

        Returns:
            security_group (SecurityGroup): The security group
    '''

    logging.info(f'Creating security group "{name}"...')
    security_group = get_security_group(ec2, name)
    if security_group is not None:
        logging.info(f'  Already exist.')
        return security_group
    security_group: SecurityGroup = ec2.create_security_group(
        GroupName=name, 
        Description='N/A'
    )
    logging.info(f'  Created.')
    return security_group





def add_tcp_rule(security_group: SecurityGroup, port: int):
    '''
    Allows all incoming TCP requests for the specified port on a security group.
    
        Parameters:
            security_group (SecurityGroup): The security group
            port (int):                     The incoming port to allow
    '''

    # Check if the rule already exist
    for ip_permission in security_group.ip_permissions:
        if ip_permission.get('IpProtocol') == 'tcp' and \
           ip_permission.get('FromPort') == port and \
           ip_permission.get('ToPort') == port:
            logging.info(f'  Rule already exist.')
            return

    # Create the new rule
    security_group.authorize_ingress(
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    logging.info(f'  Rule added.')





def add_ssh_rule(security_group: SecurityGroup):
    '''
    Allows all incoming SSH requests for on a security group.
    
        Parameters:
            security_group (SecurityGroup): The security group
    '''

    logging.info(f'{security_group.group_name}: Allowing SSH traffic...')
    add_tcp_rule(security_group, 22)





def add_http_rule(security_group: SecurityGroup):
    '''
    Allows all incoming HTTP requests for on a security group.
    
        Parameters:
            security_group (SecurityGroup): The security group
    '''

    logging.info(f'{security_group.group_name}: Allowing HTTP traffic...')
    add_tcp_rule(security_group, 80)





def add_https_rule(security_group: SecurityGroup):
    '''
    Allows all incoming HTTPS requests for on a security group.
    
        Parameters:
            security_group (SecurityGroup): The security group
    '''

    logging.info(f'{security_group.group_name}: Allowing HTTPS traffic...')
    add_tcp_rule(security_group, 443)





def add_sg_rule(security_group: SecurityGroup, from_security_group: SecurityGroup):
    '''
    Allows all requests from a security group to another.
    
        Parameters:
            security_group (SecurityGroup):      The destination group
            from_security_group (SecurityGroup): The source group
    '''

    # Check if the rule already exist
    logging.info(f'{security_group.group_name}: Allowing all traffic from "{from_security_group.group_name}"...')
    for ip_permission in security_group.ip_permissions:
        if ip_permission.get('IpProtocol') == '-1' and \
           ip_permission.get('FromPort') is None and \
           ip_permission.get('ToPort') is None and \
           ip_permission.get('UserIdGroupPairs') is not None:
            for user_id_group_pair in ip_permission.get('UserIdGroupPairs'):
                if user_id_group_pair['GroupId'] == from_security_group.group_id:
                    logging.info(f'  Rule already exist.')
                    return
    
    # Create the new rule
    security_group.authorize_ingress(
        IpPermissions=[
            {
                'IpProtocol': '-1',
                'FromPort': -1,
                'ToPort': -1,
                'UserIdGroupPairs': [{ 'GroupId': from_security_group.group_id }]
            }
        ],
    )
    logging.info(f'  Rule added.')
    return