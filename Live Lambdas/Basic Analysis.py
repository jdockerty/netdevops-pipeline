"""
###############


THIS FILE SERVES AS A WAY TO VIEW THE LIVE LAMBDA FUNCTION CORRESPONDING TO THE BASIC ANALYSIS FOR A CF FILE.


###############
"""

import json
import boto3
import os
import tempfile
import zipfile

# Ensures that CodePipeline and S3 are accessible globally.
code_pipeline = boto3.client('codepipeline')
s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                  aws_secret_access_key=os.environ['secret_access_key'])


def parse_CF_basic_check(job, resources_data):
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
    for key in resources_data.keys():
        print(resources_data[key]['Type'])

        if 'AWS::EC2::Instance' in resources_data[key]['Type']:
            print(resources_data[key]['Properties'])
            try:
                does_ami_exists = resources_data[key]['Properties']['ImageId']
                data_response['{}-EC2Instance'.format(key)] = 'ImageId is {}'.format(does_ami_exists)
            except KeyError:
                data_response['{}-EC2Instance'.format(key)] = 'ERROR: An AMI must be specified.'
                pipeline_job_fail(job)
                return data_response

        if 'AWS::EC2::SecurityGroup' in resources_data[key]['Type']:
            try:
                group_desc_exists = resources_data[key]['Properties']['GroupDescription']
                data_response['{}-SecurityGroup'.format(key)] = 'GroupDescription is {}'.format(group_desc_exists)
                if 'SecurityGroupIngress' in resources_data[key]['Properties']:
                    print("Ingress: ", resources_data[key]['Properties']['SecurityGroupIngress'])

                    for ingress_rule in resources_data[key]['Properties']['SecurityGroupIngress']:
                        if ingress_rule['IpProtocol'] == -1:
                            data_response[
                                '{}-SecurityGroupIngress'] = 'ERROR: IpProtocol should not be -1, this is completely open.'
                            pipeline_job_fail(job)
                            return data_response

                if 'SecurityGroupEgress' in resources_data[key]['Properties']:
                    print("Egress: ", resources_data[key]['Properties']['SecurityGroupEgress'])
                    for egress_rule in resources_data[key]['Properties']['SecurityGroupEgress']:
                        if egress_rule['IpProtocol'] == -1:
                            data_response[
                                '{}-SecurityGroupEgress'] = 'ERROR: IpProtocol should not be -1, this is completely open.'
                            pipeline_job_fail(job)
                            return data_response

            except KeyError:
                data_response['{}-SecurityGroup'] = 'ERROR: A GroupDescription must be added.'
                pipeline_job_fail(job)
                return data_response

    pipeline_job_success(job)
    print("End of function")
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
        parse_CF_basic_check(job_id, CF_resources)
    except Exception as e:
        # Any sort of error being raised will cause the job to fail.
        print("Error: ", str(e))
        pipeline_job_fail(job_id)