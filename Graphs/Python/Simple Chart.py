import boto3
import matplotlib.pyplot as plt

def data_vis_setup(x,y):
    """Simple setup function for pyplot chart.

    Args:
    x: Data set for plotting the x axis.
    y: Data set for plotting the y axis.

    Returns:
    True: Boolean value is returned when the function executes successfully.

    """

    plt.style.use('seaborn-whitegrid')
    plt.xlabel("Test Timestamp")
    plt.ylabel("Error Count")
    plt.title("Error count plotted against timestamps of test occurrences.")
    plt.grid()
    plt.plot(x, y)
    return True

dynamodb = boto3.resource('dynamodb')
data = dynamodb.Table('Pipeline_response_data')
my_data = data.scan(AttributesToGet=['Error Count', 'Time'])
errors = []
timestamps = []

for entries in my_data['Items']:
    print(entries['Time'], entries['Error Count'])
    errors.append(int(entries['Error Count']))
    timestamps.append(entries['Time'])

data_vis_setup(timestamps,errors)