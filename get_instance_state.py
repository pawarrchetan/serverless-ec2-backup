import boto3

def get_instance_state(fid):
    ec2 = boto3.client('ec2')
    ec2status = ec2.describe_instance_status(InstanceIds=[
        fid],)
    ec2state = ''
    for i in ec2status["InstanceStatuses"]:
        # ec2state = i["InstanceState"]["Name"]
        ec2state = i["InstanceState"]
    return ec2state


# ua9Fp2p2dX1NaIt1dCzz

def get_instance_status(fid):
    ec2 = boto3.client('ec2')
    ec2status = ec2.describe_instances(InstanceIds=[fid])
    ec2state = ''
    for i in ec2status["Reservations"]:
        ec2state = i["Instances"][0]["State"]["Name"]
    return ec2state

# print(response_one)

if __name__ == '__main__':
  state = get_instance_status("i-091a65ffb10564b88")
  print(state)