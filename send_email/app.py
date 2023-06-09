import json
import os

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from jinja2 import Environment, select_autoescape, FileSystemLoader
from simple_ses_mailer.mailers import SesEmailMessage


sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),
    integrations=[
        AwsLambdaIntegration(),
    ],
    traces_sample_rate=1.0
)


def lambda_handler(event, context):
    http_method = event.get('httpMethod')

    # Basic ping response
    if http_method == 'GET':
        return {
            "statusCode": 200,
            "body": json.dumps({
                'success': True,
                'message': 'Service online',
            }),
        }

    # Processing POST request json data
    if http_method == 'POST':
        request_body = event.get('body')
        request_headers = event.get('headers')

        if not request_headers['Content-Type'] == 'application/json':
            return {
                "statusCode": 200,
                "body": json.dumps({
                    'success': False,
                    'message': 'Request body should be application/json',
                }),
            }

        if request_headers['Content-Type'] == 'application/json':
            request_json = json.loads(request_body)
            your_name = request_json.get("your_name")
            if not your_name:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        'success': False,
                        'message': 'Name should be supplied',
                    }),
                }

            # Send email if name has been specified
            env = Environment(
                loader=FileSystemLoader('templates'),
                autoescape=select_autoescape(['html', 'xml'])
            )
            template = env.get_template('mail.html')
            html = template.render(name=your_name)

            msg = SesEmailMessage(
                subject='AWS Lambda Email',
                body_html=html,
                embedded_attachments_list=['templates/logo.png'],
                mail_to=os.getenv('MAIL_TO')
            )
            msg.send()

            return {
                "statusCode": 200,
                "body": json.dumps({
                    'success': True,
                    'message': 'Message sent',
                }),
            }
