# Flask `app.py``
# Create simple webserver for data query

from fastapi import FastAPI
import pandas as pd
import json

import sys
from pathlib import Path
appdir = Path(__file__).resolve().parent
sys.path.append(str(appdir))

from utils import Global_Config, InternalDatabaseConnector

app = FastAPI()
dbConnector = InternalDatabaseConnector()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/historical_dividend")
async def read_historical_dividend():
    return json.loads(
        dbConnector
        .read_sql(f"""SELECT * FROM {Global_Config.get_value("DB", "historicalDividendTableName")}""")
        .assign(**{
            "date": lambda x: pd.to_datetime(x["date"]),
            "recordDate": lambda x: pd.to_datetime(x["recordDate"]),
            "paymentDate": lambda x: pd.to_datetime(x["paymentDate"]),
            "declarationDate": lambda x: pd.to_datetime(x["declarationDate"]),
        })
        .to_json(orient="records")
    )

@app.get("/delisted")
async def read_historical_dividend():
    return json.loads(
        dbConnector
        .read_sql(f"""SELECT * FROM {Global_Config.get_value("DB", "delistedTableName")}""")
        .assign(**{
            "ipoDate": lambda x: pd.to_datetime(x["ipoDate"]),
            "delistedDate": lambda x: pd.to_datetime(x["delistedDate"]),
        })
        .to_json(orient="records")
    )
