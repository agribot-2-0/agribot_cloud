import json
import urllib.request


class Weather:
    def __init__(self, config, logger):
        self.location_id = config['location_id']
        self.api = config['api_token']
        self.data = ""
        self.logger = logger

    def request_current_conditions_data(self):
        base_url = "http://dataservice.accuweather.com/currentconditions/v1"
        self.request_data(base_url)

    def request_data(self, base_url):
        url = "{}/{}?apikey={}&details=true".format(base_url, self.location_id,
                                                    self.api)
        try:
            with urllib.request.urlopen(url) as url:
                self.data = json.loads(url.read().decode())
            return True
        except urllib.error.HTTPError as error:
            self.logger.error(error)
            return False

    def get_temperature(self):
        return self.data[0]["Temperature"]["Metric"]["Value"]

    def get_relative_humidity(self):
        return self.data[0]["RelativeHumidity"]

    def get_wind_direction(self):
        return self.data[0]["Wind"]["Direction"]["Degrees"]

    def get_wind_value(self):
        return self.data[0]["Wind"]["Speed"]["Metric"]["Value"]

    def get_pressure(self):
        return self.data[0]["Pressure"]["Metric"]["Value"]
