#!/bin/bash
cd /app
python -m backend.cron.todos
sleep 30
python -m backend.cron.erp_status_sync
sleep 30
python -m backend.cron.erp_order_id
sleep 30
python -m backend.cron.order_webhook_check
python -m backend.cron.calculate_distance
exit 0
