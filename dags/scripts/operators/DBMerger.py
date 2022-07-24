# Parse data from `Requestor` and merge into database (no duplicate)
import pandas as pd

import sys
from pathlib import Path
scripts_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(scripts_dir))

from operators.Requestor import RequestorStub, Requestor
from utils.DBConnector import LocalDatabaseConnector, InternalDatabaseConnector
from utils.GlobalConstants import Global_Config

class DBMerger(object):

    @staticmethod
    def update_historical_dividend(results, dbConnector) -> bool:
        # Parse json into pandas
        if results is None:
            return False
        try:
            symbol = results["symbol"]
            historical = results["historical"]
        except KeyError:
            return False
        df = pd.DataFrame(historical)
        df["symbol"] = symbol

        # Convert and Re-order
        df = df.assign(**{
            "date": lambda x: pd.to_datetime(x["date"]),
            "recordDate": lambda x: pd.to_datetime(x["recordDate"]),
            "paymentDate": lambda x: pd.to_datetime(x["paymentDate"]),
            "declarationDate": lambda x: pd.to_datetime(x["declarationDate"]),
        })[["symbol", "date", "label", "adjDividend", "dividend", "recordDate", "paymentDate", "declarationDate"]]
        
        # Update Table
        old_df = (
            dbConnector
            .read_sql(f"""SELECT symbol, date FROM {Global_Config.get_value("DB", "historicalDividendTableName")}""")
            .assign(**{
                "date": lambda x: pd.to_datetime(x["date"])
            })
        )
        new_df = old_df.merge(df, how="outer", indicator=True, on=["symbol", "date"]).reset_index(drop=True)
        new_df = new_df[new_df["_merge"] == "right_only"].drop(columns=["_merge"])
        with dbConnector.engine.connect() as connection:
            new_df.to_sql(
                Global_Config.get_value("DB", "historicalDividendTableName"),
                connection, if_exists="append", index=False
            )
        return len(new_df) > 0
    
    @staticmethod
    def update_delisted_companies(results, dbConnector) -> bool:
        if results is None:
            return False
        # Convert and Re-order
        df = pd.DataFrame(results).assign(**{
            "ipoDate": lambda x: pd.to_datetime(x["ipoDate"]),
            "delistedDate": lambda x: pd.to_datetime(x["delistedDate"]),
        })[["symbol", "companyName", "exchange", "ipoDate", "delistedDate"]]
        # Update Table
        old_df = (
            dbConnector
            .read_sql(f"""SELECT symbol, ipoDate, delistedDate FROM {Global_Config.get_value("DB", "delistedTableName")}""")
            .assign(**{
                "ipoDate": lambda x: pd.to_datetime(x["ipoDate"]),
                "delistedDate": lambda x: pd.to_datetime(x["delistedDate"]),
            })
        )
        new_df = old_df.merge(df, how="outer", indicator=True, on=["symbol", "ipoDate", "delistedDate"]).reset_index(drop=True)
        new_df = new_df[new_df["_merge"] == "right_only"].drop(columns=["_merge"])
        with dbConnector.engine.connect() as connection:
            new_df.to_sql(
                Global_Config.get_value("DB", "delistedTableName"),
                connection, if_exists="append", index=False
            )
        return len(new_df) > 0

if __name__ == "__main__":
    # dbConnector = LocalDatabaseConnector()
    dbConnector = InternalDatabaseConnector()

    res = RequestorStub.get_historical_dividend("AAPL")
    # res = Requestor.get_historical_dividend("MSFT")
    DBMerger.update_historical_dividend(res, dbConnector)

    res = RequestorStub.get_delist_companies(0)
    # res = Requestor.get_delist_companies(1)
    DBMerger.update_delisted_companies(res, dbConnector)
