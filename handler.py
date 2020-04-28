from datetime import datetime, timedelta
import os
import boto3
import logging
from botocore.exceptions import ClientError

RETENTION_DAYS = os.getenv('RETENTION_DAYS', 30)
# set logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)


def get_session(region):
    return boto3.session.Session(region_name=region)


def get_instance_name(fid):
    ec2 = boto3.resource('ec2')
    ec2instance = ec2.Instance(fid)
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename


# Fix bug for AMI creation of Terminating instance
# def get_instance_state(fid):
#     ec2 = boto3.client('ec2')
#     ec2status = ec2.describe_instance_status(InstanceIds=[
#         fid],)
#     instancestate = ''
#     for i in ec2status["InstanceStatuses"]:
#         instancestate = i["InstanceState"]["Name"]
#     return instancestate


# Fix bug for AMI creation of Terminating instance
def get_instance_state(fid):
    ec2 = boto3.client('ec2')
    ec2state = ec2.describe_instances(InstanceIds=[fid])
    instancestate = ''
    for i in ec2state["Reservations"]:
        instancestate = i["Instances"][0]["State"]["Name"]
    return instancestate

def cleanup(region):
    '''This method searches for all AMI images with a tag of RemoveOn
       and a value of YYYYMMDD of the day its ran on then removes it
    '''
    today = datetime.utcnow().strftime('%Y%m%d')

    session = get_session(region)
    client = session.client('ec2')
    resource = session.resource('ec2')

    images = client.describe_images(Filters=[{'Name': 'tag:RemoveOn', 'Values': [today]}])
    for image_data in images['Images']:
        image = resource.Image(image_data['ImageId'])
        name_tag = [tag['Value'] for tag in image.tags if tag['Key'] == 'Name']
        if name_tag:
            log.info(f"Deregistering {name_tag[0]}")
        image.deregister()


def backup(region):
    '''This function searches for all EC2 instances with a tag of BackUp
       and creates a AMI for them and tags the images with a
       RemoveOn tag of a YYYYMMDD value of days in UTC mentioned in RETENTION_DAYS variable from today
    '''
    created_on = datetime.utcnow().strftime('%Y%m%d%H%M')
    remove_on = (datetime.utcnow() + timedelta(days=int(RETENTION_DAYS))).strftime('%Y%m%d')
    
    session = get_session(region)
    client = session.client('ec2')
    resource = session.resource('ec2')
    
    reservations = client.describe_instances(Filters=[{'Name': 'tag-key', 'Values': ['BackUp']}])
    
    for reservation in reservations['Reservations']:
        for instance_description in reservation['Instances']:
            instance_id = instance_description['InstanceId']
            instance_state = get_instance_state(instance_id)     # Fix bug for AMI creation of Terminating instance
            if instance_state in ['running', 'stopping', 'stopped']:
                log.info(f"Instance is in status running, stopping or stopped : {instance_id}")
                name_tag = get_instance_name(instance_id)
                name = f"{name_tag}_InstanceId({instance_id})_CreatedOn({created_on})"
                log.info(f"Creating Backup: {name}")
                image_description = client.create_image(InstanceId=instance_id, Name=name, NoReboot=True)
                images = []
                images.append(image_description['ImageId'])
                image = resource.Image(image_description['ImageId'])
                log.info(f"Tagging Backup Image: {name}")
                image.create_tags(Tags=[{'Key': 'RemoveOn', 'Value': remove_on}, {'Key': 'Name', 'Value': name}])
            else:
                log.info(f"Instance is not in status running, stopping or stopped : {instance_id}")
                continue


def lambda_handler(event, context):
    '''This function acts as the handler for the lambda function to take backup of EC2 instances 
       with a tag of BackUp and creates a AMI for them and tags the images with a
       RemoveOn tag of a YYYYMMDD value of days in UTC mentioned in RETENTION_DAYS environment
       variable from today
    '''
    try:
        region = context.invoked_function_arn.split(':')[3]
        account_id = context.invoked_function_arn.split(':')[4]
        log.info("Running AMI BACKUP CREATION")
        backup(region)
        log.info("AMI BACKUP CREATION successful")
        log.info("Running AMI BACKUP CLEANUP")
        cleanup(region)
        log.info("AMI BACKUP CLEANUP successful")
        return {
                'statusCode': 200,
                'message':'Success!!!'
            }
    except ClientError as e:
        log.error("Unexpected error: %s" % e)
