import os
import pandas as pd
import sqlalchemy as sa
from typing import Union, List
from sqlalchemy import MetaData, Integer, DateTime, String, Float, Column, Table

import sys
from pathlib import Path
scripts_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(scripts_dir))

from utils.Singleton import Singleton
from utils.Logger import Logger
from utils.GlobalConstants import Global_Config

# Define Database Connectors
class DatabaseConnector():
    def read_sql(self, sql_query: Union[str, List[str]], **kwargs) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        with self.engine.connect() as connection:
            result = None
            if type(sql_query) == str:
                result = pd.read_sql(sql_query, connection, **kwargs)
            else:
                result = []
                for q in sql_query:
                    result.append(pd.read_sql(q, connection, **kwargs))
            return result

    def init_db(self, is_drop_tables: bool = True):
        """
            Initialize tables to correct schema
        """
        # Initialize SQL Database with correct schema
        logger = Logger(
            verbose = Global_Config.get_value("General", "verbose") == "True",
            debug = Global_Config.get_value("General", "debug") == "True"
        )
        # Historical Dividend Schema
        hist_div_tablename = Global_Config.get_value("DB", "historicalDividendTableName")
        hist_div_schema = [
            Column("symbol", String(30), primary_key=True),
            Column("date", DateTime, primary_key=True),
            Column("label", String(300)),
            Column("adjDividend", Float),
            Column("dividend", Float),
            Column("recordDate", DateTime),
            Column("paymentDate", DateTime),
            Column("declarationDate", DateTime),
        ]
        # Delisted Schema
        delisted_tablename = Global_Config.get_value("DB", "delistedTableName")
        delisted_schema = [
            Column("symbol", String(30), primary_key=True),
            Column("companyName", String(300)),
            Column("exchange", String(300)),
            Column("ipoDate", DateTime, primary_key=True),
            Column("delistedDate", DateTime, primary_key=True)
        ]

        for tablename, schema in [(hist_div_tablename, hist_div_schema), (delisted_tablename, delisted_schema)]:
            logger(f"[Init Database] - Checking for existing '{tablename}' table", is_debug=True)
            ins = sa.inspect(self.engine)
            is_skipping = False

            with self.engine.connect() as connection:
                if ins.dialect.has_table(self.engine.connect(), tablename):
                    if is_drop_tables:
                        # Delete Previous 
                        logger(f"[Init Database] - Dropping '{tablename}' table...!", is_debug=True)
                        connection.execute(f"DROP TABLE IF EXISTS '{tablename}'")
                    else:
                        logger(f"[Init Database] - '{tablename}' table already exists... Skipping", is_debug=True)
                        is_skipping = True
                else:
                    logger(f"[Init Database] - '{tablename}' table does not exists!", is_debug=True)
                    is_skipping = False
            
            if not is_skipping:
                logger(f"[Init Database] - Initializing new '{tablename}' table...", is_debug=True)
                metadata = MetaData(self.engine)
                ins = sa.inspect(self.engine)
                Table(tablename, metadata, *schema)
                metadata.create_all()
                logger(f"[Init Database] - Initializing '{tablename}' table complete", is_debug=True)

        logger(f"[Init Database] - Initializing database complete", is_debug=True)

class InternalDatabaseConnector(DatabaseConnector, metaclass=Singleton):
    def __init__(self, engine = None):
        super().__init__()
        # try:
        #     import pymysql
        # except ModuleNotFoundError:
        #     os.system("pip install pymysql")
        
        if engine is not None:
            self.engine = engine
        else:
            self.engine = sa.create_engine(
                f"""mysql+pymysql://{os.environ["MYSQL_USER"]}:{os.environ["MYSQL_PASSWORD"]}@database/{os.environ["MYSQL_DATABASE"]}""", echo=False
            )
        self.init_db(is_drop_tables=False)

class LocalDatabaseConnector(DatabaseConnector, metaclass=Singleton):
    # For testing - using sqlite
    def __init__(self, engine = None):
        super().__init__()
        if engine is not None:
            self.engine = engine
        else:
            self.engine = sa.create_engine(
                f"""sqlite:///{Global_Config.get_value("General", "localDatabasePath")}""", echo=False
            )
        self.init_db(is_drop_tables=False)

if __name__ == "__main__":
    LocalDatabaseConnector()