import os
import requests
import boto3
from botocore.exceptions import ClientError

AWS_REGION = "us-east-1"

RECIPIENTS = os.getenv("RECIPIENTS")
SENDER = "DAILY DINGO <jake.medal@gmail.com>"
SUBJECT = "Here's your Daily Dingo!"
CHARSET = "UTF-8"
HTML_BODY_TEMPLATE = """
    <html>
        <head></head>
        <body>
          <h1>DAILY DINGO</h1>
          <img src={}>
          </body>
    </html>
"""
NON_HTML_BODY_TEMPLATE = "Here's your image: {}"
RANDOM_DINGO_API_URL = "https://dog.ceo/api/breed/dingo/images/random"

ses_client = boto3.client('ses', region_name=AWS_REGION)


def construct_send_email_request(recipient, html_body, non_html_body):
    return {
        'Destination': {
            'ToAddresses': [
                recipient,
            ]
        },
        "Message": {
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': html_body,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': non_html_body,
                }
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            }
        },
        "Source": SENDER
    }


def lambda_handler(event, context):
    image_url = requests.get(RANDOM_DINGO_API_URL).json().get("message", "Oops, no pic this time. Sorry!")

    non_html_body = NON_HTML_BODY_TEMPLATE.format(image_url)
    print(non_html_body)
    html_body = HTML_BODY_TEMPLATE.format(image_url)
    print(html_body)

    recipients = RECIPIENTS.split(",")
    print(f"Got list of recipients: {recipients}")

    responses = []
    for recipient in recipients:
        print(f"Sending email to verified recipient: {recipient}")
        try:
            send_email_request = construct_send_email_request(recipient, html_body, non_html_body)
            response = ses_client.send_email(**send_email_request)

            print(f"Email sent! Message ID: {response['MessageId']}")
            response['Recipient'] = recipient
            responses.append(response)

        except ClientError as ce:
            print(f"A boto3 client error occurred: {ce.response['Error']['Message']}")
            if 'Email address is not verified.' in ce.response['Error']['Message']:
                print('Continuing on to try the rest of the emails.')
                continue
            else:
                raise ce
        except Exception as e:
            print(f"An unexpected exception occurred: {str(e)}")
            raise e

    return {
        'statusCode': 200,
        'imageUrl': image_url,
        'sesResponses': responses
    }


if __name__ == "__main__":
    lambda_handler(None, None)