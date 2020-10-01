from smsapi.client import SmsApiPlClient


class SmsApi:  # pylint: disable=too-few-public-methods
    def __init__(self, token):
        self.client = SmsApiPlClient(access_token=token)

    def send_sms(self, number, message_body):
        # self.client.sms.send(to=number, message=message_body)

        print("|{:<100}|".format("SMS sent to: {}| body: {}".format(
            number, message_body)))
