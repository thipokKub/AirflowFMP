# Requestor read config + query data into JSON format
# - Create Stub (Testing), and Real version

import os
import json
import requests
from time import sleep
from typing import Dict, Union

# Resolve to root directory
import sys
from pathlib import Path
curr_dir = Path(__file__).resolve().parent
parentddir = curr_dir.parent
sys.path.append(parentddir)

BASE_URI  = "https://financialmodelingprep.com/api/v3"

class RequestorStub:
    # For testing
    @staticmethod
    def get_delist_companies(page: int = 0):
        file_path: str = os.path.join(curr_dir, "samples", "sample_delisted.json")
        sleep(0.2)
        with open(file_path) as f:
            return json.load(f)
    
    @staticmethod
    def get_historical_dividend(symbol: str):
        file_path: str = os.path.join(curr_dir, "samples", "sample_historical_dividend.json")
        sleep(0.2)
        with open(file_path) as f:
            return json.load(f)

class Requestor:
    @staticmethod
    def fmp_data_request(uri_path: str, query_params: Dict[str, Union[str, int, float]] = None):
        """
            Request data from FMP server, and return as JSON (dictionary/list)
        """
        # Parsing query params
        # - Make sure 'apikey' is not overlapped
        if query_params is None:
            query_params = {}
        if "apikey" in query_params.keys():
            del query_params["apikey"]
        query_params["apikey"] = os.environ["API_KEY"]
        # Generate uri
        uri: str = f"{BASE_URI}{uri_path}"

        # Perform request
        r = requests.get(uri, params=query_params)
        if r.status_code == requests.codes.ok:
            return r.json()
        
        # Failed tp request
        # TODO: *Catch error - logging or something*
        return None 
    
    @staticmethod
    def get_delist_companies(page: int = 0):
        return Requestor.fmp_data_request("/delisted-companies", { "page": page })
    
    @staticmethod
    def get_historical_dividend(symbol: str):
        return Requestor.fmp_data_request(f"/historical-price-full/stock_dividend/{symbol}")

if __name__ == "__main__":
    print(RequestorStub.get_delist_companies(0))
    print()
    print(RequestorStub.get_historical_dividend("AAPL"))