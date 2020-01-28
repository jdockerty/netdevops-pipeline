import json
import hashlib

job_event = {
  "CodePipeline.job": {
    "data": {
      "artifactCredentials": {
        "secretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "sessionToken": "token",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
      },
      "actionConfiguration": {
        "configuration": {
          "FunctionName": "my-function",
          "UserParameters": "user-parameter-string"
        }
      },
      "inputArtifacts": [
        {
          "revision": "ca2bdeadbeef7d1932acb4977e08c803295d9896",
          "name": "input-artifact",
          "location": {
            "type": "S3",
            "s3Location": {
              "objectKey": "test/key",
              "bucketName": "example-bucket"
            }
          }
        }
      ],
      "outputArtifacts": [
        {
          "revision": 'null',
          "name": "output-artifact",
          "location": {
            "type": "S3",
            "s3Location": {
              "objectKey": "test/key2",
              "bucketName": "example-bucket2"
            }
          }
        }
      ]
    },
    "id": "c968ef10-6415-4127-80b1-42502218a8c7",
    "accountId": "123456789012"
  }
}

template_event = {'NetDevOneEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}, 'KeyName': 'NetDevKeys', 'SecurityGroupIds': [{'Ref': 'NetDevOneSG'}]}}, 'NetDevTwoEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}, 'SecurityGroupIds': [{'Ref': 'NetDevTwoSG'}]}}, 'NetDevOneVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.1.0.0/16', 'EnableDnsHostnames': True}}, 'NDOneVPCGateway': {'Type': 'AWS::EC2::InternetGateway', 'Properties': {}}, 'NDOneGatewayAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'InternetGatewayId': {'Ref': 'NDOneVPCGateway'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.2.0.0/16', 'EnableDnsHostnames': True}}, 'NetDevOneSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.1.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.2.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevVPCPeer': {'Type': 'AWS::EC2::VPCPeeringConnection', 'Properties': {'PeerVpcId': {'Ref': 'NetDevTwoVPC'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}}}, 'NetDevTwoRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevTwoRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}}}, 'NetDevOneRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '10.2.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevTwoRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'DestinationCidrBlock': '10.1.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevOneSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevOneVPC'}, 'SecurityGroupEgress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevTwoSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevTwoVPC'}, 'SecurityGroupEgress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevOneDefaultRoute': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '0.0.0.0/0', 'GatewayId': {'Ref': 'NDOneVPCGateway'}}}, 'NetDevCustGW': {'Type': 'AWS::EC2::CustomerGateway', 'Properties': {'BgpAsn': 65000, 'IpAddress': '79.69.154.80', 'Type': 'ipsec.1'}}, 'NetDevVPNGW': {'Type': 'AWS::EC2::VPNGateway', 'Properties': {'Type': 'ipsec.1'}}, 'NetDevVPNConnection': {'Type': 'AWS::EC2::VPNConnection', 'Properties': {'CustomerGatewayId': {'Ref': 'NetDevCustGW'}, 'Type': 'ipsec.1', 'VpnGatewayId': {'Ref': 'NetDevVPNGW'}}}, 'NetDevVPNAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevVPNRoutePropagation': {'Type': 'AWS::EC2::VPNGatewayRoutePropagation', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'RouteTableIds': {'Ref': 'NetDevOneRouteTable'}}, 'DependsOn': 'NetDevVPNAttach'}}
response_data_test = {'NetDevOneVPC-VPC': 'Present', 'NetDevOneVPC-VPC Properties': 'Properties exist', 'NetDevOneVPC-VPC-CidrBlock': {'10.1.0.0/16': 'PRIVATE'}, 'NDOneVPCGateway-InternetGateway': 'Properties exist', 'VPCGWAttach-VpcId': 'VpcId referenced', 'VPCGWAttach-VPN/IGW': 'VpnGatewayId or InternetGatewayId present', 'NetDevTwoVPC-VPC': 'Present', 'NetDevTwoVPC-VPC Properties': 'Properties exist', 'NetDevTwoVPC-VPC-CidrBlock': {'10.2.0.0/16': 'PRIVATE'}, 'NetDevOneRouteToTwo-RouteTableId-VpcPeeringConnection': 'Valid Route', 'NetDevTwoRouteToTwo-RouteTableId-VpcPeeringConnection': 'Valid Route', 'NetDevOneDefaultRoute-RouteTableId-VpcId': 'Valid Route', 'NetDevVPNGW-VPNGateway': 'Valid VPN type present.', 'NetDevVPNConnection-VPNConnection': 'CustomerGatewayId present.', 'NetDevVPNConnection-Transit_OR_VPNGW': 'Either TransitGatewayId or VpnGatewayId present, but not both.', 'NetDevVPNRoutePropagation-VPNGatewayRoutePropagation': 'VpnGatewayId present.', 'Errors': {'Count': '1', 'Keys with errors': ['NetDevVPNRoutePropagation']}}

context = 1

import boto3 # Not required inside of Live Lambda
import base64
from datetime import datetime

code_pipeline = boto3.client('codepipeline')
dynamodb = boto3.client('dynamodb')
job = 0

def add_to_table(hashID, response_data):
    """Add the new test to the DynamoDB table with the relevant data alongside it.

    The appropriate data is passed into the function and the relevant data at the time generated from within, such as the
    current date and time of the test. All of this data is sent to the DynamoDB table.

    The response_data is the whole response which is encoded into Base64 encoding, this provides a representation of the
    full data in the table and this can be decoded on the data visualisation side, this choice was made so as to ease
    the process of sending a map, as this is only needed occasionally, the data can be represented in others way and
    decoded when necessary.

    Args:
    hashID: A hash which is generated from the hash_data() function.
    response_data: Dictionary built from analysing the file.

    Returns:
        True: Boolean value is returned when the function executes successfully.

    """

    error_count = response_data['Errors']['Count']
    table_name = "Pipeline_response_data"
    utf8_dict = str(response_data).encode('utf-8')
    b64_dict = base64.b64encode(utf8_dict)
    time_now = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

    # This would produce the original dictionary.
    # original = eval(base64.b64decode(b64_dict))

    items = {
        'DataID': {'S': hashID},
        'Time': {'S': time_now},
        'Analysis Type': {'S': 'Basic'},
        'Full Encoded Data': {'B': b64_dict},
        'Error Count': {'N': error_count}
    }
    dynamodb.put_item(TableName=table_name, Item=items)
    return True

def hash_data(response_data):
    """Generates a SHA256 hash of the response_data dictionary to act as the primary key in the DynamoDB table.

    The response_data is hashed in order to generate an ID for the DynamoDB table. This requires the dictionary keys
    to be sorted and then encoding the dictionary as a mutable object, a JSON string representation of the data.

    Args:
    response_data: Dictionary built from analysing the file.

    Returns:
        hex_digest: A SHA256 hash based on the JSON string representation of the response_data dictionary.
    """

    string_repr = json.dumps(sorted(response_data.items()), sort_keys=True).encode('utf-8')
    hashed_data = hashlib.sha256(string_repr)
    hex_digest = hashed_data.hexdigest()
    print(hex_digest)
    return hex_digest

def parse_CF_basic_check(resources_data):
    """Parses the CloudFormation resources data for basic information.

    Some very simple checks are conducted on the Cloudformation template, this ensures that other tests are not wasted
    if the most basic checks are failed. These two tests are: when launching an EC2 instance, an AMI should be provided,
    and ensuring that a SecurityGroupIngress/Egress does not contain a completely open virtual firewall rule, as this
    allows everything instead of being granular.


    Args:
        <job_id on live Lambda>: Job_id from CodePipeline.
        resources_data: The relevant data contained from the 'Resources' key
        from the JSON CloudFormation template.

    Returns:
        data_response: A dictionary which contains the data property
        that is checked, the key, and a log about the particular property,
        this is the value. If there are any errors the job will fail and a value
        of "ERROR: [message here]" will be tied to the corresponding key.

    """
    print(resources_data)
    data_response = {}
    error_counter = 0
    error_keys = []
    for key in resources_data.keys():

        if 'AWS::EC2::Instance' in resources_data[key]['Type']:
            try:
                does_ami_exists = resources_data[key]['Properties']['ImageId']
                data_response['{}-EC2Instance'.format(key)] = 'ImageId is {}'.format(does_ami_exists)
            except KeyError:
                data_response['{}-EC2Instance'.format(key)] = {"Error": "An AMI must be specified."}
                error_counter += 1
                error_keys.append(key)

        if 'AWS::EC2::SecurityGroup' in resources_data[key]['Type']:
            try:
                group_desc_exists = resources_data[key]['Properties']['GroupDescription']
                data_response['{}-SecurityGroup'.format(key)] = 'GroupDescription is {}'.format(group_desc_exists)
                if 'SecurityGroupIngress' in resources_data[key]['Properties']:

                    for ingress_rule in resources_data[key]['Properties']['SecurityGroupIngress']:
                        if ingress_rule['IpProtocol'] == -1:
                            data_response['{}-SecurityGroupIngress'.format(key)] = {"Error": "IpProtocol should not be -1, this is completely open."}
                            error_counter += 1
                            error_keys.append(key)

                if 'SecurityGroupEgress' in resources_data[key]['Properties']:
                    for egress_rule in resources_data[key]['Properties']['SecurityGroupEgress']:
                        if egress_rule['IpProtocol'] == -1:
                            data_response['{}-SecurityGroupEgress'.format(key)] = {"Error": "IpProtocol should not be -1, this is completely open."}
                            error_counter += 1
                            error_keys.append(key)

            except KeyError:
                data_response['{}-SecurityGroup'.format(key)] = {"Error": "A GroupDescription must be added."}
                error_counter += 1
                error_keys.append(key)

    if error_counter == 0:
        data_response['Errors'] = {"Count": "{}".format(error_counter), "Keys with errors": error_keys}
        pipeline_job_success(job)
    else:
        data_response['Errors'] = {"Count": "{}".format(error_counter), "Keys with errors": error_keys}
        pipeline_job_fail(job)

    print("End of function")
    print(data_response)
    return data_response


def pipeline_job_fail(job):
    """Dummy 'pipeline fail' function call for testing Lambda locally.

    Function is only used by name so that it can be called in the appropriate place locally and then the proper
    functionality is executed inside of the Lambda.

    Args:
    job: The job_id which is being provided, locally this will be a value of 0 just for testing purposes.

    Returns:
        None
    """
    pass

def pipeline_job_success(job):
    """Dummy 'pipeline success' function call for testing Lambda locally.

    Function is only used by name so that it can be called in the appropriate place locally and then the proper
    functionality is executed inside of the Lambda.

    Args:
        job: The job_id which is being provided, locally this will be a value of 0 just for testing purposes.

    Returns:
        None
    """
    pass

hash = hash_data(response_data_test)
print(parse_CF_basic_check(template_event))
add_to_table(hash, response_data_test)