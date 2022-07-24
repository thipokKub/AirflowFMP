# Handle all DB Queries (frontend API)

# Parse data from `Requestor` and merge into database (no duplicate)
import pandas as pd

import sys
from pathlib import Path
scripts_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(scripts_dir))

from utils.DBConnector import LocalDatabaseConnector, InternalDatabaseConnector
from utils.GlobalConstants import Global_Config

class DBQuery(object):

    @staticmethod
    def read_all_hist_div(dbConnector):
        return (
            dbConnector
            .read_sql(f"""SELECT * FROM {Global_Config.get_value("DB", "historicalDividendTableName")}""")
            .assign(**{
                "date": lambda x: pd.to_datetime(x["date"]),
                "recordDate": lambda x: pd.to_datetime(x["recordDate"]),
                "paymentDate": lambda x: pd.to_datetime(x["paymentDate"]),
                "declarationDate": lambda x: pd.to_datetime(x["declarationDate"]),
            })
        )
    
    @staticmethod
    def read_all_delisted(dbConnector):
        return (
            dbConnector
            .read_sql(f"""SELECT * FROM {Global_Config.get_value("DB", "delistedTableName")}""")
            .assign(**{
                "ipoDate": lambda x: pd.to_datetime(x["ipoDate"]),
                "delistedDate": lambda x: pd.to_datetime(x["delistedDate"]),
            })
        )

if __name__ == "__main__":
    # dbConnector = LocalDatabaseConnector()
    dbConnector = InternalDatabaseConnector()
    print(DBQuery.read_all_hist_div(dbConnector))
    print(DBQuery.read_all_delisted(dbConnector))