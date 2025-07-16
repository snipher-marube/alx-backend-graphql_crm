#!/usr/bin/env python3
"""
GraphQL Order Reminder Script
Sends reminders for pending orders from the last 7 days
"""
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import os

# GraphQL endpoint configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def get_recent_orders():
    """Query recent orders using GraphQL"""
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    query = gql("""
    query {
        orders(filter: {order_date_gt: "%s"}, status: "pending") {
            id
            customer {
                email
            }
            order_date
        }
    }
    """ % seven_days_ago)

    return client.execute(query)

def log_reminders(orders):
    """Log order reminders to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n[{timestamp}] Order Reminders:\n")
        for order in orders['orders']:
            log_entry = (f"Order ID: {order['id']}, "
                        f"Customer Email: {order['customer']['email']}, "
                        f"Date: {order['order_date']}\n")
            f.write(log_entry)

if __name__ == "__main__":
    try:
        orders = get_recent_orders()
        log_reminders(orders)
        print("Order reminders processed!")
    except Exception as e:
        print(f"Error processing order reminders: {str(e)}")