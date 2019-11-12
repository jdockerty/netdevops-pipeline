import json


event = {
  "name": "Jack"
}
context = 1

def lambda_handler(event,context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello {}, from Lambda!'.format(event['name']))
    }   


print(lambda_handler(event,context))

