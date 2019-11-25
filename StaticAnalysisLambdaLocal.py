import json
import boto3
import os

event = {
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
context = 1
import json
import boto3
import os
from nested_lookup import nested_lookup
from collections.abc import Iterable

code_pipeline = boto3.client('codepipeline')


def get_resources(event):
    s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                      aws_secret_access_key=os.environ['secret_access_key'])
    bucket_name = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']['bucketName']
    data_key = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']['objectKey']
    data_object = s3.get_object(Bucket=bucket_name, Key=data_key)
    data_obj_body = data_object['Body']
    print("Body: ", data_obj_body)
    print("JSON: ", json.load(data_obj_body, strict=False))
    print(type(data_obj_body))

    # content = json.loads(data_object['Body'].read().decode('utf-8', 'ignore'))
    # print("Content Type: ", type(content))
    # print(content)
    # print("JSON Content: ", json.load(content))
    # return (content['Resources'])


def flatten_list(nested_obj):
    flat_list = []

    if isinstance(nested_obj, list):
        for item in nested_obj:
            if isinstance(item, Iterable) and not isinstance(item, str):
                flat_list.extend(flatten_list(item))
            else:
                flat_list.append(item)
        return flat_list

    elif isinstance(nested_obj, dict):
        for item in nested_obj.items():
            if isinstance(item, dict) and not isinstance(item, str):
                flat_list.extend(flatten_list(item))
            else:
                flat_list.append(item)
        return flat_list


def parse_CF_basic_SG(resources_data):
    standard_keys_check = ['SecurityGroupIngress',
                           'SecurityGroupEgress']

    counter = 1
    response_data = {}
    for keys_to_check in standard_keys_check:
        key_val_list = flatten_list(nested_lookup(keys_to_check, resources_data))
        try:
            for key, value in key_val_list:
                if key == 'IpProtocol' and value == -1:
                    # Stops the ports being complete open, -1 indicates all ports
                    response_data['SG_SIMPLE_TEST'] = [
                        {'Job_ID': "IpProtocol_test_{}".format(counter), "Result": "Fail"}]
                    return response_data
                else:
                    response_data['SG_SIMPLE_TEST'] = [
                        {'Job_ID': "IpProtocol_test_{}".format(counter), "Result": "Pass"}]
                    return response_data
        except ValueError:
            for value in key_val_list:
                if '255.255.255.255' in value:
                    # Fail is there a destination to a broadcast address, this shouldn't be allowed.
                    response_data['DESTINATION_SIMPLE_TEST'] = [
                        {'Job_ID': "Destination_test_{}".format(counter), "Result": "Fail"}]
                    return response_data
                else:

                    response_data['DESTINATION_SIMPLE_TEST'] = [
                        {'Job_ID': "Destination_test_{}".format(counter), "Result": "Pass"}]

        counter += 1


def parse_CF_network(resources_data):
    for key in resources_data.keys():

        # Ensure that a Route contains either a RouteTableId AND VpcPeeringConnectionId or VpcId.
        if 'EC2::Route' in resources_data[key]['Type']:
            if 'RouteTableId' in resources_data[key]['Properties'] and 'VpcPeeringConnectionId' in resources_data[key][
                'Properties']:
                # add pipeline success method here and to others.
                print("Valid Route")
            elif 'RouteTableId' in resources_data[key]['Properties'] and 'VpcId' in resources_data[key]['Properties']:
                print("Valid Route")
            else:
                # pipeline_job_fail()
                return 'Failed'


def pipeline_job_fail(job):
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'type': 'JobFailed', 'message': 'string',
                                                                    'externalExecutionId': 'string'})
    return


def pipeline_job_success(job):
    code_pipeline.put_job_success_result(jobId=job)
    return


def static_analysis_file(event, context):
    try:
        job_id = event['CodePipeline.job']['id']
        CF_resources = get_resources(event)
        check_basic_SG = parse_CF_basic_SG(CF_resources)
        SG_result = check_basic_SG['SG_SIMPLE_TEST'][0]['Result']
        if SG_result == 'Fail':
            pipeline_job_fail(job_id)
            return 'File did not meet the criteria.'
        else:
            pipeline_job_success(job_id)
            # parse_CF_network(CF_resources)
            return 'Pass'
    except Exception as e:
        print("Error: ", e)
        pipeline_job_fail(job_id)

static_analysis_file(event,context)

