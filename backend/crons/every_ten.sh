#!/bin/bash
cd /app
python -m backend.cron.kp_status_change
python -m backend.cron.close_felmeres
python -m backend.cron.create_order
python -m backend.cron.close_todo
python -m backend.cron.paid_invoice
python -m backend.cron.check_invoice
exit 0
