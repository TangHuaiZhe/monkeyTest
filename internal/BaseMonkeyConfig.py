from typing import Dict, Any
import configparser
import os


def getConfig():
    upperDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(upperDir, "monkey.ini")


def monkeyConfig():
    config = configparser.ConfigParser()
    config.read(getConfig())
    appConfig: Dict[str, Any] = {"package_name": config['DEFAULT']['package_name'],
                                 "key": config['DEFAULT']['key'],
                                 "cmd": config['DEFAULT']['cmd'] + ">"}
    return appConfig


if __name__ == '__main__':
    print(getConfig())
    monkeyConfig()
    print(os.path.join(os.getcwd(), "monkey111.ini"))
