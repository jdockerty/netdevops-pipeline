import json
import boto3
import os
import tempfile
import zipfile
import hashlib
import base64
from datetime import datetime
from IPy import IP

# Ensures that CodePipeline and S3 are accessible globally.
code_pipeline = boto3.client('codepipeline')
s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                  aws_secret_access_key=os.environ['secret_access_key'])

dynamodb = boto3.client('dynamodb')


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
        'Analysis Type': {'S': 'Network'},
        'Full Encoded Data': {'B': b64_dict},
        'Error Count': {'N': error_count}
    }
    dynamodb.put_item(TableName=table_name, Item=items)
    print("Data sent to DynamoDB table: ", table_name)
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
    print("Hash generated: ", hex_digest)
    return hex_digest


def network_check(job, resources_data):
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
    error_counter = 0
    error_keys = []
    for key in resources_data.keys():

        if 'AWS::EC2::VPC' == resources_data[key]['Type']:
            data_response['{}-VPC'.format(key)] = "Present"
            try:
                vpc_properties = resources_data[key]['Properties']
                data_response['{}-VPC Properties'.format(key)] = "Properties exist"
                if 'CidrBlock' in vpc_properties:
                    if IP(vpc_properties['CidrBlock']).iptype() != "PRIVATE":
                        error_counter += 1
                        data_response['{}-VPC-CidrBlock'.format(key)] = {
                            "Error": "IP Addresses should only be RFC1918 compliant.",
                            "Address Type": IP(vpc_properties['Cidr_block']).iptype()}
                        error_keys.append(key)
                    else:
                        data_response['{}-VPC-CidrBlock'.format(key)] = \
                            {vpc_properties['CidrBlock']: IP(vpc_properties['CidrBlock']).iptype()}

            except KeyError:
                data_response['{}-VPC'.format(key)] = {"Error": "VPC Property was not present."}
                error_counter += 1
                error_keys.append(key)

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
                data_response['{}-RouteTableId'.format(key)] = \
                    {"Error": "Either property was not present in the EC2::Route."}
                error_counter += 1
                error_keys.append(key)

        if 'EC2::InternetGateway' in resources_data[key]['Type']:
            try:
                # InternetGateway must have a Properties key, even if it is blank with an empty dict {}.
                should_exist = resources_data[key]['Properties']
                data_response['{}-InternetGateway'.format(key)] = "Properties exist"
            except KeyError:
                data_response['{}-InternetGateway'.format(key)] = {
                    "Error": "VpnGatewayId or InternetGatewayId not present."}
                error_counter += 1
                error_keys.append(key)

        if 'EC2::VPCGatewayAttachment' in resources_data[key]['Type']:
            if 'VpcId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VpcId'] = "VpcId referenced"
            if 'VpnGatewayId' in resources_data[key]['Properties'] or \
                    'InternetGatewayId' in resources_data[key]['Properties']:
                data_response['VPCGWAttach-VPN/IGW'] = "VpnGatewayId or InternetGatewayId present"
            else:
                data_response['{}-VPCGWAttach'.format(key)] = {
                    "Error": "VpnGatewayId or InternetGatewayId not present."}
                error_keys.append(key)
                error_counter += 1

        if 'AWS::EC2::VPNGateway' == resources_data[key]['Type']:
            if 'Type' in resources_data[key]['Properties']:
                if resources_data[key]['Properties']['Type'] != "ipsec.1":
                    data_response['{}-VPNGateway'.format(key)] = {"Error": "The only allowed type is 'ipsec.1'."}
                    error_keys.append(key)
                    error_counter += 1
                else:
                    data_response['{}-VPNGateway'.format(key)] = "Valid VPN type present."

        if 'AWS::EC2::VPNGatewayRoutePropagation' == resources_data[key]['Type']:
            if 'RouteTableIds' in resources_data[key]['Properties']:
                if isinstance(resources_data[key]['Properties']['RouteTableIds'], list):
                    data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "Value is list of strings."
                else:
                    data_response['{}-VPNGatewayRoutePropagation'.format(key)] = {
                        "Error": "Value must be list of string corresponding to RouteTableIds."}
                    error_counter += 1
                    error_keys.append(key)
            if 'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = "VpnGatewayId present."
            else:
                data_response['{}-VPNGatewayRoutePropagation'.format(key)] = {"Error": "VpnGatewayId is required."}
                error_counter += 1
                error_keys.append(key)

        if 'AWS::EC2::VPNConnection' == resources_data[key]['Type']:
            if 'CustomerGatewayId' in resources_data[key]['Properties']:
                data_response['{}-VPNConnection'.format(key)] = "CustomerGatewayId present."

            if 'TransitGatewayId' in resources_data[key]['Properties'] and \
                    'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-Transit_AND_VPNGW'.format(key)] = {
                    "Error": "Both TransitGatewayId AND VpnGatewayId cannot be used within the VPNConnection Type."}
                error_keys.append(key)
                error_counter += 1

            if 'TransitGatewayId' in resources_data[key]['Properties'] or \
                    'VpnGatewayId' in resources_data[key]['Properties']:
                data_response['{}-Transit_OR_VPNGW'.format(
                    key)] = "Either TransitGatewayId or VpnGatewayId present, but not both."

    if error_counter == 0:
        data_response['Errors'] = {"Count": "{}".format(error_counter), "Keys with errors": error_keys}
        pipeline_job_success(job)
    else:
        data_response['Errors'] = {"Count": "{}".format(error_counter), "Keys with errors": error_keys}
        pipeline_job_fail(job)
    print("End of check function")
    print(data_response)
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
        s3_data = event['CodePipeline.job']['data']['inputArtifacts'][0]
        CF_resources = json.loads(get_template_from_zip(s3_data))['Resources']
        network_template_data = network_check(job_id, CF_resources)
        print(network_template_data)
        hash_result = hash_data(network_template_data)
        add_to_table(hash_result, network_template_data)
        print("End of Lambda.")
    except Exception as e:
        # Any sort of error being raised will cause the job to fail and the error is printed.
        print("Error: ", str(e))
        pipeline_job_fail(job_id)