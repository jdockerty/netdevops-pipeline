import json
import boto3
import os

event = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "eu-west-2",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "projectpipelinesource",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::example-bucket"
        },
        "object": {
          "key": "TestEnvCF.json",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
context = 1
def read_local_creds(file="LocalCredentials"):
    cred_list = []
    with open(file) as creds:
        for line in creds:
            cred_list.append(line.strip("\n\r"))

    return cred_list

def get_resources(event):
  s3 = boto3.client('s3', aws_access_key_id=read_local_creds()[0],
                    aws_secret_access_key=read_local_creds()[1])
  # in Lambda this becomes environment variables os.environ['access_key'] and os.environ['secret_access_key']

  bucket_name = event['Records'][0]['s3']['bucket']['name']
  data_key = event['Records'][0]['s3']['object']['key']
  data_object = s3.get_object(Bucket=bucket_name, Key=data_key)
  content = json.loads(data_object['Body'].read())
  return (content['Resources'])


def static_analysis_file(event, context):
  CF_resources = get_resources(event)
  print(CF_resources)


static_analysis_file(event,context)

