# src/orchestration.py

from prefect import flow, task
from prefect_shell import ShellOperation


@task(retries=2, retry_delay_seconds=900)
def run_daily_builtin():
    ShellOperation(
        command=(
            "source /path/to/venv/bin/activate && "
            "cd /path/to/daily_trader && "
            "python -m src.main"
        ),
        return_all=True,
    )()


@flow(name="daily-trading-flow", retries=0)
def trading_flow():
    run_daily_builtin()


if __name__ == "__main__":
    trading_flow()
