import json
import urllib.request


class Weather:
    def __init__(self):
        self.location_id = "2-273125_1_AL"
        self.api = "AGRIBOT_CONFIGURE_LOCALLY"
        self.data = ""

    def request_current_conditions_data(self):
        base_url = "http://dataservice.accuweather.com/currentconditions/v1"
        self.request_data(base_url)

    def request_data(self, base_url):
        url = "{}/{}?apikey={}&details=true".format(base_url, self.location_id,
                                                    self.api)
        with urllib.request.urlopen(url) as url:
            self.data = json.loads(url.read().decode())
        # print(self.data)

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
