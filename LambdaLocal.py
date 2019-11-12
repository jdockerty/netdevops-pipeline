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
          "key": "YAML/TestEnvCF.yml",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
context = 1
#AKIAT5HAPIXFC2GUTN6E
#GTr1GN4aBI69DZcWWmn7NuUX+T/vZQwKvrgHr76a

def static_analysis_file(event,context):
    s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'],
                      aws_secret_access_key=os.environ['secret_access_key'])

    data = s3.get_object(Bucket='projectpipelinesource', Key='YAML/TestEnvCF.yml')
    content = data['Body'].read()
    return str(content)
    # bucket_name = s3.Object(event['Records'][0]['s3']['bucket']['name'])
    # data_object = s3.Object(event['Records'][0]['s3']['object']['key'])
    # object_body = data_object.get()['Body'].read()




static_analysis_file(event,context)

