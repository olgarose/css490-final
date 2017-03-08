import os
import sys
from pathlib import Path
import json
from pprint import pprint
import arrow
import boto3


def send_text(phone_num, message):
    access_key, secret_key = os.environ['AWS_PARAMS'].split(';')
    client = boto3.client(
        'sns',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    resp = client.publish(
        PhoneNumber=phone_num,
        Message=message,
        MessageAttributes={
            'SMSType': {
                'StringValue': 'Promotional',
                'DataType': 'String',
            }
        }
    )
    pprint(resp)
    return resp


if __name__ == '__main__':
    number = sys.argv[1]
    output = send_text(number, "It's time to go to sleep! You have a busy day tomorrow.")
