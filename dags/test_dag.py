from airflow.decorators import dag, task
from datetime import datetime, date, timedelta

default_args = {
    'owner': 'fmp_airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 7, 22)
}

@dag('hello_world', schedule_interval='@daily', default_args=default_args, catchup=False)
def hello_world():

    @task
    def hello_world():
        print("Hello World!")
        return True
    
    hello_world()

dag = hello_world()