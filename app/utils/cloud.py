import boto3
from app.utils import config

boto = boto3.Session(region_name=config.AWS_REGION)


# ----------------------------------------------------------------------------------------------------------------------
#                                                      SES
# ----------------------------------------------------------------------------------------------------------------------

def send_email(subject, from_address, to_address, html, text, reply_to_address=None):
    if config.ENVIRONMENT != "production":
        to_address = config.EMAIL_TESTING_ADDRESS
    if reply_to_address:
        reply_to = [reply_to_address]
    else:
        reply_to = []
    ses = boto.client("ses")
    ses.send_email(
        Source=from_address,
        ReplyToAddresses=reply_to,
        Destination={"ToAddresses": [to_address]},
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Html": {"Data": html},
                "Text": {"Data": text}
            }
        }
    )
