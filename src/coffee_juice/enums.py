from enum import Enum


class AppEnvEnum(Enum):
    prod = 'prod'
    stage = 'stage'
    test = 'test'


class DrinkType(Enum):
    coffee = 'coffee'
    juice = 'juice'
    water = 'water'
    other = 'other'


class HealthStatus(Enum):
    ok = 'OK'
    not_connection = 'NO CONNECTION'


class ExampleEnum(Enum):
    example = 'example'
