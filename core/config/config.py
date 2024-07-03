import json
import platform
import secrets

from core.constants.constants import CONFIGPATH

def createConfig(server_name:str, key_lenght:int):
    server_config = {
        "server_name" : server_name,
        "hex_encryption_key":secrets.token_hex(key_lenght)
    }
    
    if platform.system().lower() == "windows":
        try:
            with open(CONFIGPATH, "w+", encoding="UTF-8") as file:
                json.dump(server_config)
            
            return True
        except Exception as e:
            return e


def loadConfig():
    if platform.system().lower() == "windows":
        try:
            with open(CONFIGPATH, mode="r", encoding="UTF-8") as config_file:
                config = json.load(config_file)

            return config
        except FileNotFoundError:
            return "config not found"