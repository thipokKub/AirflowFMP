# AirflowFMP
AIrflow + Financial Modeling Prep API sample project

This is a sample project for data crawling using Airflow framework for task monitoring
The API is based on [Financial Modeling Prep API](https://site.financialmodelingprep.com/) using free-tier account

In this project, there are `2` main endpoints crawler
1. **Historical Dividend** - This follows the past dividend of specific companies, which is defined in `dags/configs/config.ini` like so
    ```
    [Historical]
    symbols=AAPL,MSFT,AMZN
    ```
    the above is the default (sample) companies, which are Apple Inc. (AAPL), Microsoft Corp (MSFT), and Amazon (AMZN)
2. **Delisted Companies** - This endpoint returned all previously delisted companies up to around 2000s

I decided to modify [airflow official docker](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html), by adding additional container for `mysql` database, and `fastAPI` webserver. Even though, it is possible to use database provided in the `docker-compose.yml`, I personally think that still is a good idea to separate airflow operational database from webserver database

All of the sensitive credentals can be found in `.env.dev`. Pushing this file to public repo is generally not a good idea. However because this is a sample project, and I use a burner account, there is no harm of doing so (just specific to this case)

If you are planning to use any of these, please change the credentials information within `.env.dev`

---

To run the system, make sure docker is running, and for Apple Silicon users `colima` is your friend

- To initialize, run `init.sh` script
- To start, run `run.sh` script
- To stop, run `stop.sh` script
- To reset data, run `purge.sh` script
