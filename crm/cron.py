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