# Define
# - Global variable e.g. Config
# - Custom typing

# from enum import Enum

import os
import sys
from pathlib import Path
curr_file_path = Path(__file__)
scripts_dir = curr_file_path.resolve().parent.parent
configs_dir = scripts_dir.parent
sys.path.append(str(scripts_dir))

# Local import
from utils.ConfigParser import Config

# Define constants / global variables
CONFIG_FILE_PATH = os.path.join(configs_dir, "configs", "config.ini")
Global_Config = Config(config_file=CONFIG_FILE_PATH)

if __name__ == "__main__":
    print([symbol.strip().upper() for symbol in Global_Config.get_value("Historical", "symbols").strip().split(",")])