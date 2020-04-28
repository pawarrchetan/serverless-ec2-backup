import json
import boto3
from pprint import pprint

def test(fid):
    # TODO implement
    client = boto3.client("ec2")
    status = client.describe_instance_status(InstanceIds=[
        fid],)
    #pprint(status)
    for i in status["InstanceStatuses"]:
        # print("AvailabilityZone :", i["AvailabilityZone"])
        # print("InstanceId :", i["InstanceId"])
        print("InstanceState :", i["InstanceState"]["Name"])
        # print("InstanceStatus", i["InstanceStatus"])
    return i["InstanceState"]["Name"]


if __name__ == '__main__':
  state = test("i-07883ccad4f26aa38")
  print(state)

# Fix bug for AMI creation of Terminating instance
def get_instance_state(fid):
    ec2 = boto3.client('ec2')
    ec2state = ec2.describe_instances(InstanceIds=[fid])
    instancestate = ''
    for i in ec2state["Reservations"]:
        instancestate = i["Instances"][0]["State"]["Name"]
    return instancestate