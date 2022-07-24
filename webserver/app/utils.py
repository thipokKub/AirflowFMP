import os
import configparser

import os
import pandas as pd
import sqlalchemy as sa
from datetime import datetime
from typing import Union, List
from sqlalchemy import MetaData, Integer, DateTime, String, Float, Column, Table

import sys
from pathlib import Path
appdir = Path(__file__).resolve().parent
sys.path.append(str(appdir))

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

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

CONFIG_FILE_PATH = os.path.join(appdir, "config.ini")
Global_Config = Config(config_file=CONFIG_FILE_PATH)

class Logger(object, metaclass=Singleton):
    
    def __init__(self, verbose: bool = True, debug: bool = True):
        self.verbose = verbose
        self.debug = debug
        
    def __call__(self, string: str, is_debug: bool = False):
        if self.verbose and ((is_debug and self.debug) or (not is_debug)):
            print(f"[{datetime.now().isoformat()}] [{'DEBUG' if is_debug else 'LOG'}]: {string}")

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
        
        if engine is not None:
            self.engine = engine
        else:
            self.engine = sa.create_engine(
                f"""mysql+pymysql://{os.environ["MYSQL_USER"]}:{os.environ["MYSQL_PASSWORD"]}@database/{os.environ["MYSQL_DATABASE"]}""", echo=False
            )
        self.init_db(is_drop_tables=False)
