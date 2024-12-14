#!/bin/bash
cd /app
python -m backend.cron.feed_process
exit 0
