from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """Generates weekly CRM report via GraphQL"""
    log_file = "/tmp/crm_report_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql("""
        query {
            totalCustomers
            totalOrders
            totalRevenue
        }
        """)
        
        result = client.execute(query)
        
        report = (
            f"{timestamp} - Report: "
            f"{result['totalCustomers']} customers, "
            f"{result['totalOrders']} orders, "
            f"${result['totalRevenue']:,.2f} revenue"
        )
        
        with open(log_file, "a") as f:
            f.write(report + "\n")
        
        return report
    
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Report generation failed: {str(e)}\n")
        raise