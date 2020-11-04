import json
import datetime
import urllib.request


class Weather:
    def __init__(self, config, logger):
        self.location_id = config['location_id']
        self.api = config['api_token']
        self.data = ""
        self.logger = logger

    def request_current_conditions_data(self):
        base_url = "http://dataservice.accuweather.com/currentconditions/v1"
        return self.request_data(base_url)

    def request_one_day_hourly_forecast_data(self):
        base_url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour"
        return self.request_data(base_url)

    def request_data(self, base_url):
        url = "{}/{}?apikey={}&details=true&metric=true".format(
            base_url, self.location_id, self.api)
        try:
            with urllib.request.urlopen(url) as url:
                self.data = json.loads(url.read().decode())
            return True
        except urllib.error.HTTPError as error:
            self.logger.error(error)
            return False

    def get_forecast_temperature(self):
        return self.get_forecast_data("Temperature")

    def get_forecast_humidity(self):
        forecast_dict = {}
        for table_element in self.data:
            forecast_dict[self.str_to_time(
                table_element["DateTime"])] = table_element["RelativeHumidity"]
        return forecast_dict

    def get_forecast_wind_speed(self):
        forecast_dict = {}
        for table_element in self.data:
            forecast_dict[self.str_to_time(
                table_element["DateTime"]
            )] = table_element["Wind"]["Speed"]["Value"]
        return forecast_dict

    def get_forecast_data(self, element_name):
        forecast_dict = {}
        for table_element in self.data:
            forecast_dict[self.str_to_time(
                table_element["DateTime"]
            )] = table_element[element_name]["Value"]
        return forecast_dict

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

    @staticmethod
    def if_weather_condition_fullfiled(forecast, condition, value_str):
        value = float(value_str)
        if condition == "less":
            return {k: v for (k, v) in forecast.items() if v < value}
        if condition == "more":
            return {k: v for (k, v) in forecast.items() if v > value}
        if condition == "equal":
            return {k: v for (k, v) in forecast.items() if v == value}

        return {}

    @staticmethod
    def str_to_time(date_str, date_format="%Y-%m-%dT%H%M%S%z"):
        return datetime.datetime.strptime(date_str.replace(":", ""),
                                          date_format)
