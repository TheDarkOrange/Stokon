#!/usr/bin/env bash
# scripts/run_daily.sh

set -euo pipefail

source /path/to/venv/bin/activate
cd /path/to/Stokon

LOGDIR=/var/log/stokon
mkdir -p "$LOGDIR"

echo "===== $(date) Starting daily job =====" >> "$LOGDIR/trading.log"
python -m src.main --dry-run >> "$LOGDIR/trading.log" 2>&1
EXIT=$?
echo "===== $(date) Finished with exit code $EXIT =====" >> "$LOGDIR/trading.log"

if [ "$EXIT" -ne 0 ]; then
    echo "Daily job failed with code $EXIT. Check logs." | mailx -s "Stokon Failure" you@example.com
fi

exit $EXIT
