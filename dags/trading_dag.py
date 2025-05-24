import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator

# Use the Asia/Jerusalem timezone
local_tz = pendulum.timezone("Asia/Jerusalem")

default_args = {
    "owner": "trading-team",
    "depends_on_past": False,
    "email": ["you@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": pendulum.duration(minutes=15),
}

with DAG(
    dag_id="daily_equities_trading",
    description="Run daily EOD trading job",
    schedule_interval="15 18 * * 1-5",  # Mon–Fri at 18:15 Asia/Jerusalem
    start_date=pendulum.datetime(2025, 6, 1, tz=local_tz),
    catchup=False,
    default_args=default_args,
    tags=["trading", "daily"],
) as dag:

    run_trading = BashOperator(
        task_id="run_daily_trading",
        bash_command=(
            "source /path/to/venv/bin/activate && "
            "cd /path/to/daily_trader && "
            "python -m src.main"
        ),
    )

    notify_success = EmailOperator(
        task_id="notify_success",
        to="you@example.com",
        subject="[Trading DAG] Success: {{ ds }}",
        html_content=(
            "Daily trading job completed successfully on {{ ds }}."
        ),
    )

    run_trading >> notify_success
