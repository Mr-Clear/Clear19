import json
from configparser import ConfigParser


class Config:
    @staticmethod
    def _config() -> ConfigParser:
        config = ConfigParser()
        config.read('clear19.ini')
        return config

    @staticmethod
    def locale() -> str:
        return Config._config()['General']['locale']

    class DateTime:
        @staticmethod
        def date_format() -> str:
            return Config._config()['DateTime']['date_format']

        @staticmethod
        def time_format() -> str:
            return Config._config()['DateTime']['time_format']

        @staticmethod
        def date_time_format() -> str:
            return Config._config()['DateTime']['date_time_format']

    class Weather:
        @staticmethod
        def city_code() -> str:
            return Config._config()['Weather']['wetter.com_city_code']

        @staticmethod
        def temp_values_url() -> str:
            return Config._config()['Weather']['temp_values']

    class FritzBox:
        @staticmethod
        def address() -> str:
            return Config._config()['FritzBox']['address']

        @staticmethod
        def password() -> str:
            return Config._config()['FritzBox']['password']

    class DiskStats:
        @staticmethod
        def drives() -> dict[str, str]:
            return json.loads(Config._config()['DiskStats']['drives'])
