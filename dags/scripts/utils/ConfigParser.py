import os
import configparser

import sys
from pathlib import Path
curr_file_path = Path(__file__)
parentddir = curr_file_path.resolve().parent.parent # scripts dir
sys.path.append(str(parentddir))

# Local import
from utils.Singleton import Singleton

class Config(object, metaclass=Singleton):
    def __init__(
        self, config_file: str
    ):
        if not os.path.exists(config_file):
            # Create empty file
            with open(config_file) as handle:
                handle.write('')
        
        self._config_file = config_file
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)

    def reload(self):
        # Just in case, force reloading config file
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)
        
    def get_config(self) -> configparser.ConfigParser:
        return self._config
    
    def save_config(self, config: configparser.ConfigParser = None) -> bool:
        with open(self._config_file, "r+") as handle:
            if config is None:
                self._config.write(handle)
            else:
                config.write(handle)
        return True
    
    def get_section(self, section_name) -> configparser.SectionProxy:
        try:
            return self._config[section_name]
        except KeyError:
            return None
    
    def get_value(self, section_name, key):
        try:
            return self._config[section_name][key]
        except KeyError:
            return None
    
    def del_value(self, section_name, key) -> bool:
        try:
            del self._config[section_name][key]
            self.save_config()
            return True
        except KeyError:
            return False
    
    def set_value(self, section_name, key, value) -> bool:
        try:
            self._config[section_name]
        except KeyError:
            self._config[section_name] = {}
        
        self._config[section_name][key] = value
        return self.save_config()
    
    def del_section(self, section_name) -> bool:
        try:
            del self._config[section_name]
            self.save_config()
            return True
        except KeyError:
            return False
        
    def __str__(self):
        out = ""
        for sk in list(self._config.keys()):
            out += f"\n> [{sk}]\n"
            for vk in list(self._config[sk].keys()):
                out += f"\t- `{vk}`: `{self._config[sk][vk]}`\n"
        return out[1:]

if __name__ == "__main__":
    import os
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent.parent
    config_path = os.path.join(base_dir, "configs", "config.ini")

    config = Config(config_file=config_path)

    print([symbol.strip().upper() for symbol in config.get_value("Historical", "symbols").strip().split(",")])

    