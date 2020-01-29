import json
import boto3
import os
import tempfile
import zipfile
import hashlib
from datetime import datetime

# Ensures that CodePipeline, S3, and DynamoDB are accessible globally.
code_pipeline = boto3.client('codepipeline')
s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                  aws_secret_access_key=os.environ['secret_access_key'])

dynamodb = boto3.client('dynamodb')


def add_to_table(hashID, response_data):
    """Add the new test to the DynamoDB table with the relevant data alongside it.

    The appropriate data is passed into the function and the relevant data at the time generated from within, such as the
    current date and time of the test. All of this data is sent to the DynamoDB table.

    The response_data is the whole response, serialised as JSON string. This provides a representation of the
    full data in the table and can be decoded when necessary for log purposes.

    Args:
    hashID: A hash which is generated from the hash_data() function.
    response_data: Dictionary built from analysing the file.

    Returns:
        True: Boolean value is returned when the function executes successfully.

    """

    error_count = response_data['Errors']['Count']
    table_name = "Pipeline_response_data"
    json_repr = json.dumps(response_data)
    time_now = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

    items = {
        'DataID': {'S': hashID},
        'Time': {'S': time_now},
        'Check Type': {'S': 'Basic'},
        'Full JSON Data': {'S': json_repr},
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


def basic_check(job, resources_data):
    """Parses the CloudFormation resources data for basic information.

    Some very simple checks are conducted on the Cloudformation template, this ensures that other tests are not wasted
    if the most basic checks are failed. These two tests are: when launching an EC2 instance, an AMI should be provided,
    and ensuring that a SecurityGroupIngress/Egress does not contain a completely open virtual firewall rule, as this
    allows everything instead of being granular.


    Args:
        job: job_id from CodePipeline.
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
                            data_response['{}-SecurityGroupIngress'.format(key)] = {
                                "Error": "IpProtocol should not be -1, this is completely open."}
                            error_counter += 1
                            error_keys.append(key)

                if 'SecurityGroupEgress' in resources_data[key]['Properties']:
                    for egress_rule in resources_data[key]['Properties']['SecurityGroupEgress']:
                        if egress_rule['IpProtocol'] == -1:
                            data_response['{}-SecurityGroupEgress'.format(key)] = {
                                "Error": "IpProtocol should not be -1, this is completely open."}
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

    print("End of check function")
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
                                             'message': 'Job-Fail',
                                             'externalExecutionId': 'Test'})

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


def static_analysis_file(event, context):
    try:
        job_id = event['CodePipeline.job']['id']
        print("Job id:", job_id)
        # CF_resources = get_resources(event)
        s3_data = event['CodePipeline.job']['data']['inputArtifacts'][0]
        CF_resources = json.loads(get_template_from_zip(s3_data))['Resources']
        print(CF_resources)
        data_result = basic_check(job_id, CF_resources)
        print(data_result)
        hash_result = hash_data(data_result)
        add_to_table(hash_result, data_result)
        print("End of Lambda.")
    except Exception as e:
        # Any sort of error being raised will cause the job to fail.
        print("Error: ", str(e))
        pipeline_job_fail(job_id)