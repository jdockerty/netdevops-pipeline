from IPy import IP

event = {'NetDevOneEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}, 'KeyName': 'NetDevKeys', 'SecurityGroupIds': [{'Ref': 'NetDevOneSG'}]}}, 'NetDevTwoEC2': {'Type': 'AWS::EC2::Instance', 'Properties': {'InstanceType': 't2.micro', 'ImageId': 'ami-00e8b55a2e841be44', 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}, 'SecurityGroupIds': [{'Ref': 'NetDevTwoSG'}]}}, 'NetDevOneVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.1.0.0/16', 'EnableDnsHostnames': True}}, 'NDOneVPCGateway': {'Type': 'AWS::EC2::InternetGateway', 'Properties': {}}, 'NDOneGatewayAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'InternetGatewayId': {'Ref': 'NDOneVPCGateway'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoVPC': {'Type': 'AWS::EC2::VPC', 'Properties': {'CidrBlock': '10.2.0.0/16', 'EnableDnsHostnames': True}}, 'NetDevOneSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.1.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevTwoSubnetOne': {'Type': 'AWS::EC2::Subnet', 'Properties': {'CidrBlock': '10.2.0.0/24', 'MapPublicIpOnLaunch': True, 'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevVPCPeer': {'Type': 'AWS::EC2::VPCPeeringConnection', 'Properties': {'PeerVpcId': {'Ref': 'NetDevTwoVPC'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevOneRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'SubnetId': {'Ref': 'NetDevOneSubnetOne'}}}, 'NetDevTwoRouteTable': {'Type': 'AWS::EC2::RouteTable', 'Properties': {'VpcId': {'Ref': 'NetDevTwoVPC'}}}, 'NetDevTwoRTAssoc': {'Type': 'AWS::EC2::SubnetRouteTableAssociation', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'SubnetId': {'Ref': 'NetDevTwoSubnetOne'}}}, 'NetDevOneRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '10.2.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevTwoRouteToTwo': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevTwoRouteTable'}, 'DestinationCidrBlock': '10.1.0.0/16', 'VpcPeeringConnectionId': {'Ref': 'NetDevVPCPeer'}}}, 'NetDevOneSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevOneVPC'}, 'SecurityGroupEgress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': 22, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}, {'IpProtocol': 80, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevTwoSG': {'Type': 'AWS::EC2::SecurityGroup', 'Properties': {'GroupDescription': 'NetDev SG', 'VpcId': {'Ref': 'NetDevTwoVPC'}, 'SecurityGroupEgress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}], 'SecurityGroupIngress': [{'IpProtocol': -1, 'FromPort': 0, 'ToPort': 65535, 'CidrIp': '0.0.0.0/0'}]}}, 'NetDevOneDefaultRoute': {'Type': 'AWS::EC2::Route', 'Properties': {'RouteTableId': {'Ref': 'NetDevOneRouteTable'}, 'DestinationCidrBlock': '0.0.0.0/0', 'GatewayId': {'Ref': 'NDOneVPCGateway'}}}, 'NetDevCustGW': {'Type': 'AWS::EC2::CustomerGateway', 'Properties': {'BgpAsn': 65000, 'IpAddress': '79.69.154.80', 'Type': 'ipsec.1'}}, 'NetDevVPNGW': {'Type': 'AWS::EC2::VPNGateway', 'Properties': {'Type': 'ipsec.1'}}, 'NetDevVPNConnection': {'Type': 'AWS::EC2::VPNConnection', 'Properties': {'CustomerGatewayId': {'Ref': 'NetDevCustGW'}, 'Type': 'ipsec.1', 'VpnGatewayId': {'Ref': 'NetDevVPNGW'}}}, 'NetDevVPNAttach': {'Type': 'AWS::EC2::VPCGatewayAttachment', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'VpcId': {'Ref': 'NetDevOneVPC'}}}, 'NetDevVPNRoutePropagation': {'Type': 'AWS::EC2::VPNGatewayRoutePropagation', 'Properties': {'VpnGatewayId': {'Ref': 'NetDevVPNGW'}, 'RouteTableIds': [{'Ref': 'NetDevOneRouteTable'}]}, 'DependsOn': 'NetDevVPNAttach'}}
context = 1
job_id = 0
def pipeline_job_fail(job):
    pass

def pipeline_job_success(job):
    pass

def parse_network_CF(resources_data):
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

    pipeline_job_success(job_id)
    print("End of function")
    print(data_response)
    return data_response


parse_network_CF(event)
