from smsapi.client import SmsApiPlClient


class SmsApi:  # pylint: disable=too-few-public-methods
    def __init__(self, config, logger):
        self.client = SmsApiPlClient(access_token=config['sms_api_pl_token'])
        self.debug_mode = config['debug_mode']
        self.logger = logger

    def send_sms(self, number, message_body):
        if self.debug_mode:
            self.logger.warning("Debug mode")
        else:
            self.client.sms.send(to=number, message=message_body)

        self.logger.info("|{:<100}|".format("SMS sent to: {}| body: {}".format(
            number, message_body)))
