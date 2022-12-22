import os, json, logging
from typing import Dict
from boto3_type_annotations.ec2 import Client, ServiceResource


def initialize_keypair(ec2_client: Client, ec2_service_resource: ServiceResource, name: str) -> Dict:
    
    # Try to retrieve the key locally
    keypair_path = f'keypairs/{name}.json'
    keypair = None
    try:
        if os.path.isfile(f'keypairs/{name}.json'):
            logging.info(f'Reading existing keypair...')
            with open(f'keypairs/{name}.json', 'r') as file:
                keypair = json.load(file)
                logging.info(f'  Keypair loaded.')
    except:
        pass

    # If we are unable to retrieve the keypair, generate it
    if keypair is None:
        logging.info(f'Creating a new keypair...')
        # Deleting old keypair with the same name if any.
        try:
            existing_keypair = ec2_service_resource.KeyPair(name)
            existing_keypair.load()
            existing_keypair.delete()
            logging.info('  Deleted old keypair.')
        except:
            pass
        keypair = ec2_client.create_key_pair(KeyName=name)
        logging.info(f'  New keypair created.')

    # Save it
    with open(f'keypairs/{name}.json', 'w') as file:
        json.dump(keypair, file)
    
    return keypair