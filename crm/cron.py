#!/usr/bin/env python3
"""
CRM Heartbeat Logger
Logs system health every 5 minutes
"""
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import os

def log_crm_heartbeat():
    """Logs CRM heartbeat and checks GraphQL endpoint"""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Basic heartbeat logging
    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")
    
    # Optional GraphQL endpoint check
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        result = client.execute(query)
        if result.get('hello'):
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint responsive\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {str(e)}\n")


from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def update_low_stock():
    """Updates low stock products via GraphQL mutation"""
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        mutation = gql("""
        mutation {
            updateLowStockProducts {
                products {
                    name
                    stock
                }
                message
            }
        }
        """)
        
        result = client.execute(mutation)
        
        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] Low Stock Update Results:\n")
            f.write(f"Message: {result['updateLowStockProducts']['message']}\n")
            for product in result['updateLowStockProducts']['products']:
                f.write(f"Product: {product['name']}, New Stock: {product['stock']}\n")
    
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error updating low stock products: {str(e)}\n")