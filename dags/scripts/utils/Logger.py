from datetime import datetime

import sys
from pathlib import Path
scripts_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(scripts_dir))

from utils.Singleton import Singleton

class Logger(object, metaclass=Singleton):
    
    def __init__(self, verbose: bool = True, debug: bool = True):
        self.verbose = verbose
        self.debug = debug
        
    def __call__(self, string: str, is_debug: bool = False):
        if self.verbose and ((is_debug and self.debug) or (not is_debug)):
            print(f"[{datetime.now().isoformat()}] [{'DEBUG' if is_debug else 'LOG'}]: {string}")