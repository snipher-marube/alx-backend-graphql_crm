#!/bin/bash

# Clean inactive customers script
# Deletes customers with no orders in the past year

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(
    orders__isnull=True,
    last_order_date__lt=one_year_ago
).delete()

print(inactive_customers[0])  # Returns count of deleted objects
EOF
)

# Log the results
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> $LOG_FILE