# Crawler DAG
# - Crawl until the current one length is 0

import os
import pandas as pd
import sqlalchemy as sa
from airflow.decorators import dag, task
from datetime import datetime, date, timedelta

from scripts.utils.Logger import Logger
from scripts.utils.GlobalConstants import Global_Config
from scripts.utils.DBConnector import InternalDatabaseConnector
from scripts.operators.Requestor import Requestor
from scripts.operators.DBMerger import DBMerger

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 7, 22)
}

@dag('Delisted_companies_daily_update', schedule_interval='@daily', default_args=default_args, catchup=False)
def delisted_update_daily_dag():
    logger = Logger(
        verbose = Global_Config.get_value("General", "verbose") == "True",
        debug = Global_Config.get_value("General", "debug") == "True"
    )
    dbConnector = InternalDatabaseConnector()
    
    @task
    def update():
        curr_page = 0
        while True:
            logger(f"[Delisted Companies] - Quering delisted companies, page {curr_page}...", is_debug=False)
            res = Requestor.get_delist_companies(curr_page)
            if res is None or len(res) == 0: # Complete
                break
            logger(f"[Delisted Companies] - Updating delisted companies", is_debug=False)
            is_success = DBMerger.update_delisted_companies(res, dbConnector)
            if not is_success:
                break
            curr_page += 1

            if curr_page >= 3: # For testing
                logger(f"[Delisted Companies] - Daily early exit", is_debug=True)
            
        logger(f"[Delisted Companies] - Daily update complete", is_debug=False)
    
    update()

dag = delisted_update_daily_dag()

if __name__ == "__main__":
    delisted_update_daily_dag()