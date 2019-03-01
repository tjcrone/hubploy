"""
Setup authentication from various providers
"""
import subprocess
import os
from hubploy.config import get_config
import json

def registry_auth(deployment):
    """
    Do appropriate registry authentication for given deployment
    """
    config = get_config(deployment)

    if 'images' in config and 'registry' in config['images']:
        registry = config['images']['registry']
        provider = registry.get('provider')
        if provider == 'gcloud':
            registry_auth_gcloud(
                deployment, **registry['gcloud']
            )
        elif provider == 'aws':
            registry_auth_aws(
                deployment, **registry['aws']
            )
        else:
            raise ValueError(f'Unknown provider {provider} found in hubploy.yaml')


def registry_auth_gcloud(deployment, project, service_key):
    """
    Setup GCR authentication with a service_key

    This changes *global machine state* on where docker can push to!
    """
    service_key_path = os.path.join(
        'deployments', deployment, 'secrets', service_key
    )
    subprocess.check_call([
        'gcloud', 'auth',
        'activate-service-account',
        '--key-file', os.path.abspath(service_key_path)
    ])

    subprocess.check_call([
        'gcloud', 'auth', 'configure-docker'
    ])


def registry_auth_aws(deployment, project, service_key):
    """
    Setup AWS authentication with a service_key

    This changes *global machine state* on where docker can push to!
    """

    service_key_path = os.path.join(
        'deployments', deployment, 'secrets', service_key
    )

    if not os.path.isfile(service_key_path):
        raise FileNotFoundError(f'The service_key file {service_key_path} does not exist')

    # amazon-ecr-credential-helper needs this env var when run
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = os.path.abspath(service_key_path)

    # Now using amazon-ecr-credential-helper
    dockerConfig = os.path.join(os.path.expanduser('~'), '.docker', 'config.json')
    with open(dockerConfig, 'w') as f:
        json.dump(dict(credstore='ecr-login'), f)


def cluster_auth(deployment):
    """
    Do appropriate cluster authentication for given deployment
    """
    config = get_config(deployment)

    if 'cluster' in config:
        cluster = config['cluster']
        provider = cluster.get('provider')
        if provider == 'gcloud':
            cluster_auth_gcloud(
                deployment, **cluster['gcloud']
            )
        elif provider == 'aws':
            cluster_auth_aws(
                deployment, **cluster['aws']
            )
        else:
            raise ValueError(f'Unknown provider {provider} found in hubploy.yaml')


def cluster_auth_gcloud(deployment, project, cluster, zone, service_key):
    """
    Setup GKE authentication with service_key

    This changes *global machine state* on what current kubernetes cluster is!
    """
    service_key_path = os.path.join(
        'deployments', deployment, 'secrets', service_key
    )
    subprocess.check_call([
        'gcloud', 'auth',
        'activate-service-account',
        '--key-file', os.path.abspath(service_key_path)
    ])

    subprocess.check_call([
        'gcloud', 'container', 'clusters',
        f'--zone={zone}',
        f'--project={project}',
        'get-credentials', cluster
    ])


def cluster_auth_aws(deployment, project, cluster, zone, service_key):
    """
    Setup AWS authentication with service_key

    This changes *global machine state* on what current kubernetes cluster is!
    """
    service_key_path = os.path.join(
        'deployments', deployment, 'secrets', service_key
    )

    if not os.path.isfile(service_key_path):
        raise FileNotFoundError(f'The service_key file {service_key_path} does not exist')

    aws_env = os.environ.copy()
    aws_env['AWS_SHARED_CREDENTIALS_FILE'] = os.path.abspath(service_key_path)

    subprocess.check_call([
        'aws', 'eks',
        'update-kubeconfig',
        '--name', cluster
    ], env=aws_env)
