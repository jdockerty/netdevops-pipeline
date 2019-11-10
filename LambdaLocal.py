import json


event = {
  "name": "Jack"
}
def lambda_handler(event,context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
context = 1
print(lambda_handler(event,context))

