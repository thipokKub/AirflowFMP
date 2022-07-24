# Crawler DAG
# - Loop all companies name from Global_Config

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

@dag('historical_dividend_daily_update', schedule_interval='@daily', default_args=default_args, catchup=False)
def historical_dividend_daily_dag():
    logger = Logger(
        verbose = Global_Config.get_value("General", "verbose") == "True",
        debug = Global_Config.get_value("General", "debug") == "True"
    )
    dbConnector = InternalDatabaseConnector()
    company_symbols = [symbol.strip().upper() for symbol in Global_Config.get_value("Historical", "symbols").strip().split(",")]
    
    logger(f"[Historical Dividend] - Processing '{', '.join(company_symbols)}' dividend...", is_debug=False)

    @task
    def update():
        for symbol in company_symbols:
            logger(f"[Historical Dividend] - Quering '{symbol}' dividend...", is_debug=False)
            res = Requestor.get_historical_dividend(symbol)
            logger(f"[Historical Dividend] - Updating '{symbol}' dividend", is_debug=False)
            DBMerger.update_historical_dividend(res, dbConnector)
            logger(f"[Historical Dividend] - Added to '{symbol}' dividend DB", is_debug=False)
        logger(f"[Historical Dividend] - Daily update complete", is_debug=False)
    
    update()

dag = historical_dividend_daily_dag()

if __name__ == "__main__":
    historical_dividend_daily_dag()