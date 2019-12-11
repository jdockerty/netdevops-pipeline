"""
###############


THIS FILE SERVES AS A WAY TO VIEW THE LIVE LAMBDA FUNCTION CORRESPONDING TO THE NETWORK ANALYSIS FOR A CF FILE.


###############
"""

import json
import boto3
import os
import tempfile
import zipfile
from IPy import IP

# Ensures that CodePipeline and S3 are accessible globally.
code_pipeline = boto3.client('codepipeline')
s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                  aws_secret_access_key=os.environ['secret_access_key'])


def parse_CF_network(job, resources_data):
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
        job: Job_id from CodePipeline.
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

        if 'AWS::EC2::VPC' == resources_data[key]['Type']:
            data_response['{}-VPC'.format(key)] = "Present"
            try:
                vpc_properties = resources_data[key]['Properties']
                data_response['{}-VPC Properties'.format(key)] = "Properties exist"
                if 'CidrBlock' in vpc_properties:
                    if IP(vpc_properties['CidrBlock']).iptype() != "PRIVATE":
                        pipeline_job_fail(job)
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
                pipeline_job_fail(job)
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
                pipeline_job_fail(job)
                return data_response

        if 'EC2::VPCGatewayAttachment' in resources_data[key]['Type']:
            if 'VpcId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VpcId'] = "VpcId referenced"
            if 'VpnGatewayId' in resources_data[key]['Properties'] or \
                    'InternetGatewayId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VPN/IGW'] = "VpnGatewayId or InternetGatewayId present"
            else:
                pipeline_job_fail(job)
                data_response['{}-VPCGWAttach'.format(key)] = "ERROR: VpnGatewayId or InternetGatewayId not present"
                print(data_response)
                return data_response

        if 'AWS::EC2::VPNGateway' == resources_data[key]['Type']:
            if 'Type' in resources_data[key]['Properties']:
                if resources_data[key]['Properties']['Type'] != "ipsec.1":
                    data_response['{}-VPNGateway'.format(key)] = "ERROR: The only allowed type is 'ipsec.1'."
                    pipeline_job_fail(job)
                    return data_response
                else:
                    data_response['{}-VPNGateway'.format(key)] = "Valid VPN type present."

        if 'AWS::EC2::VPNGatewayRoutePropagation' == resources_data[key]['Type']:
            if 'RouteTableIds' in resources_data[key]['Properties']:
                if isinstance(resources_data[key]['Properties']['RouteTableIds'], list):

                    data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "Value is list of strings."
                else:
                    data_response['{}-VPNGatewayRoutePropagation'.format(
                        key)] = "ERROR: Value must be list of string corresponding to RouteTableIds"
                    pipeline_job_fail(job)
            if 'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "VpnGatewayId present."
            else:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "ERROR: VpnGatewayId is required."
                pipeline_job_fail(job)
                return data_response

        if 'AWS::EC2::VPNConnection' == resources_data[key]['Type']:
            if 'CustomerGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNConnection'.format(key)] = "CustomerGatewayId present."

            if 'TransitGatewayId' in resources_data[key]['Properties'] and \
                    'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-Transit_AND_VPNGW'.format(
                    key)] = "ERROR: Both TransitGatewayId AND VpnGatewayId cannot be used within the VPNConnection Type."
                pipeline_job_fail(job)
                return data_response

            if 'TransitGatewayId' in resources_data[key]['Properties'] or \
                    'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-Transit_OR_VPNGW'.format(
                    key)] = "Either TransitGatewayId or VpnGatewayId present, but not both."

    pipeline_job_success(job)
    print("End of parse function")
    return data_response


def get_template_from_zip(s3_event_data):
    """Gets the template artifact

    Downloads the artifact from the S3 artifact store to a temporary file
    then extracts the zip and returns the file containing the CloudFormation
    template.

    Args:
        s3_event_data: Takes the event data from lambda and parses the
        appropriate s3 object using the key and bucket name.

    Returns:
        The CloudFormation template as a string

    Raises:
        Exception: Any exception thrown while downloading the artifact or unzipping it

    """
    tmp_file = tempfile.NamedTemporaryFile()
    bucket = s3_event_data['location']['s3Location']['bucketName']
    print("Bucket: ", bucket)
    key = s3_event_data['location']['s3Location']['objectKey']
    print("Object Key: ", key)
    with tempfile.NamedTemporaryFile() as tmp_file:
        print("Retrieving s3://" + bucket + "/" + key)
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            print("List of archive: ", zip.namelist())
            zip.printdir()
            return zip.read(zip.namelist()[0])


def pipeline_job_fail(job):
    """Puts a failed job to CodePipeline.

    Sends the jobId and failureDetails to CodePipeline, any failed job will
    cause the pipeline to stop immediately.

    Args:
        job: The job_id is passed as the job parameter for use with placing the
        relevant job in a failed state.

    Returns:
        True: the function was executed successfully.

    """
    code_pipeline.put_job_failure_result(jobId=job,
                                         failureDetails={
                                             'type': 'JobFailed',
                                             'message': 'See data_response for further details.',
                                             'externalExecutionId': 'Test-1'})

    return True


def pipeline_job_success(job):
    """Puts a successful job to CodePipeline.

    Sends the jobId to CodePipeline, the successful job will move the pipeline
    onto the next stage.

    Args:
        job: The job_id is passed as the job parameter for use with placing the
        relevant job in a successful state.

    Returns:
        True: the function was executed successfully.

    """
    code_pipeline.put_job_success_result(jobId=job)
    return True


def network_analysis(event, context):
    try:
        job_id = event['CodePipeline.job']['id']
        print("Job id:", job_id)
        # CF_resources = get_resources(event)
        s3_data = event['CodePipeline.job']['data']['inputArtifacts'][0]
        CF_resources = json.loads(get_template_from_zip(s3_data))['Resources']
        print(CF_resources)
        network_template_data = parse_CF_network(job_id, CF_resources)
        print(network_template_data)
        return CF_resources
        # check_network_info = parse_CF_network(CF_resources)

        # if SG_result == 'Fail':
        #     pipeline_job_fail(job_id)
        #     return 'File did not meet the criteria.'
        # else:
        #     pipeline_job_success(job_id)
        #     return 'File met criteria, moved to network analysis action.'

    except Exception as e:
        # Any sort of error being raised will cause the job to fail and the error is printed.
        print("Error: ", str(e))
        pipeline_job_fail(job_id)