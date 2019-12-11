from IPy import IP

event = {'NetDevOneEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}, 'KeyName': 'NetDevKeys', 'SecurityGroupIds': [{'Ref': 'NetDevOneSG'}]}}, 'NetDevTwoEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}, 'SecurityGroupIds': [{'Ref': 'NetDevTwoSG'}]}}, 'NetDevOneVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.1.0.0/16', 'EnableDnsHostnames': True}}, 'NDOneVPCGateway': {'Type': 'AWS::EC2::InternetGateway', 'Properties': {}}, 'NDOneGatewayAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'InternetGatewayId': {'Ref': 'NDOneVPCGateway'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.2.0.0/16', 'EnableDnsHostnames': True}}, 'NetDevOneSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.1.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.2.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevVPCPeer': {'Type': 'AWS::EC2::VPCPeeringConnection', 'Properties': {'PeerVpcId': {'Ref': 'NetDevTwoVPC'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}}}, 'NetDevTwoRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevTwoRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}}}, 'NetDevOneRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '10.2.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevTwoRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'DestinationCidrBlock': '10.1.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevOneSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevOneVPC'}, 'SecurityGroupEgress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevTwoSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevTwoVPC'}, 'SecurityGroupEgress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevOneDefaultRoute': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '0.0.0.0/0', 'GatewayId': {'Ref': 'NDOneVPCGateway'}}}, 'NetDevCustGW': {'Type': 'AWS::EC2::CustomerGateway', 'Properties': {'BgpAsn': 65000, 'IpAddress': '79.69.154.80', 'Type': 'ipsec.1'}}, 'NetDevVPNGW': {'Type': 'AWS::EC2::VPNGateway', 'Properties': {'Type': 'ipsec.1'}}, 'NetDevVPNConnection': {'Type': 'AWS::EC2::VPNConnection', 'Properties': {'CustomerGatewayId': {'Ref': 'NetDevCustGW'}, 'Type': 'ipsec.1', 'VpnGatewayId': {'Ref': 'NetDevVPNGW'}}}, 'NetDevVPNAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevVPNRoutePropagation': {'Type': 'AWS::EC2::VPNGatewayRoutePropagation', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'RouteTableIds': {'Ref': 'NetDevOneRouteTable'}}, 'DependsOn': 'NetDevVPNAttach'}}
context = 1
job_id = 0
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

def parse_network_CF(resources_data):
    """Parses the CloudFormation resources data for network information.

    Various checks are conducted on the Cloudformation template within the scope
    of network related issues. The various Type keys are used from the JSON
    which is passed and they are iterated over, various criteria is checked if
    they are present. Any issue will cause the pipeline to fail and a
    dictionary, data_response, containing the checks and other log information
    will be returned. The pipeline will receive a successful job if the end of
    the function is reached without any issues, data_response is also returned
    in this case for logging purposes.


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
    data_response = {}
    for key in resources_data.keys():
        print(resources_data[key]['Type'])

        if 'AWS::EC2::VPC' == resources_data[key]['Type']:
            data_response['{}-VPC'.format(key)] = "Present"
            try:
                vpc_properties = resources_data[key]['Properties']
                data_response['{}-VPC Properties'.format(key)] = "Properties exist"
                if 'CidrBlock' in vpc_properties:
                        if IP(vpc_properties['CidrBlock']).iptype() != "PRIVATE":
                            pipeline_job_fail(job_id)
                            print("Only RFC1918 addresses should be utilised within a VPC.")
                            data_response['{}-VPC-CidrBlock'.format(key)] = \
                                "ERROR: Only RFC1918 addresses should be utilised within a VPC."
                            return data_response
                        else:
                            data_response['{}-VPC-CidrBlock'.format(key)] = \
                                {vpc_properties['CidrBlock']: IP(vpc_properties['CidrBlock']).iptype()}

            except KeyError:
                print("Properties is required within a VPC as a CidrBlock is a mandatory element.")
                data_response['{}-VPC'.format(key)] = "ERROR: VPC Property was not present."

        if 'AWS::EC2::Route' == resources_data[key]['Type']:
            if 'RouteTableId' in resources_data[key]['Properties'] and \
                    'VpcPeeringConnectionId' in resources_data[key]['Properties']:
                data_response['{}-RouteTableId-VpcPeeringConnection'.format(key)] = "Valid Route"

            elif 'RouteTableId' in resources_data[key]['Properties'] and \
                    'VpcId' in resources_data[key]['Properties']:
                data_response['{}-RouteTableId-VpcId'.format(key)] = "Valid Route"

            elif 'RouteTableId' in resources_data[key]['Properties']:
                data_response['{}-RouteTableId-VpcId'.format(key)] = "Valid Route"

            else:
                pipeline_job_fail(job_id)
                data_response['{}-RouteTableId'.format(key)] = \
                    "ERROR: Either property was not present in the EC2::Route."
                return data_response

        if 'EC2::InternetGateway' in resources_data[key]['Type']:
            try:
                # InternetGateway must have a Properties key, even if it is blank with an empty dict {}.
                should_exist = resources_data[key]['Properties']
                data_response['{}-InternetGateway'.format(key)] = "Properties exist"
            except KeyError:
                print("The IGW should contain a 'Properties' key, it can be left blank ( {} ), but it must exist.")
                data_response['{}-InternetGateway'.format(key)] = "ERROR: VpnGatewayId or InternetGatewayId not present"
                pipeline_job_fail(job_id)
                return data_response

        if 'EC2::VPCGatewayAttachment' in resources_data[key]['Type']:
            if 'VpcId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VpcId'] = "VpcId referenced"
            if 'VpnGatewayId' in resources_data[key]['Properties'] or \
                    'InternetGatewayId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VPN/IGW'] = "VpnGatewayId or InternetGatewayId present"
            else:
                pipeline_job_fail(job_id)
                data_response['{}-VPCGWAttach'.format(key)] = "ERROR: VpnGatewayId or InternetGatewayId not present"
                print(data_response)
                return data_response

        if 'AWS::EC2::VPNGateway' == resources_data[key]['Type']:
            if 'Type' in resources_data[key]['Properties']:
                if resources_data[key]['Properties']['Type'] != "ipsec.1":
                    data_response['{}-VPNGateway'.format(key)] = "ERROR: The only allowed type is 'ipsec.1'."
                    pipeline_job_fail(job_id)
                    return data_response
                else:
                    data_response['{}-VPNGateway'.format(key)] = "Valid VPN type present."

        if 'AWS::EC2::VPNGatewayRoutePropagation' == resources_data[key]['Type']:
            if 'RouteTableIds' in resources_data[key]['Properties']:
                if isinstance(resources_data[key]['Properties']['RouteTableIds'], list):

                    data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "Value is list of strings."
                else:
                    data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "ERROR: Value must be list of string corresponding to RouteTableIds"
                    pipeline_job_fail(job_id)
            if 'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "VpnGatewayId present."
            else:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "ERROR: VpnGatewayId is required."
                pipeline_job_fail(job_id)
                return data_response

        if 'AWS::EC2::VPNConnection' == resources_data[key]['Type']:
            if 'CustomerGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNConnection'.format(key)] = "CustomerGatewayId present."

            if 'TransitGatewayId' in resources_data[key]['Properties'] and \
                'VpnGatewayId' in resources_data[key]['Properties']:
                    data_response['{}-Transit_AND_VPNGW'.format(key)] = "ERROR: Both TransitGatewayId AND VpnGatewayId cannot be used within the VPNConnection Type."
                    pipeline_job_fail(job_id)
                    return data_response

            if 'TransitGatewayId' in resources_data[key]['Properties'] or \
                'VpnGatewayId' in resources_data[key]['Properties']:
                    data_response['{}-Transit_OR_VPNGW'.format(key)] = "Either TransitGatewayId or VpnGatewayId present, but not both."

    pipeline_job_success(job_id)
    print("End of function")
    print(data_response)
    return data_response


parse_network_CF(event)
