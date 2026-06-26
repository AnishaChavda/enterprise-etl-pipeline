import requests
import json
import os
import random
from datetime import datetime, timedelta

def extract_zendesk_data():
    print("Zendesk Extraction Started")
    
    # We will use the JSONPlaceholder comments endpoint to simulate ticket data
    url = "https://jsonplaceholder.typicode.com/comments"
    
    response = requests.get(url)
    print("Zendesk API Status Code:", response.status_code)
    
    comments = response.json()
    # Take 30 items to mock Zendesk tickets
    raw_tickets = comments[:30]
    
    structured_tickets = []
    
    # Generate structured mock ticket fields mapped from the raw comments
    for i, item in enumerate(raw_tickets):
        ticket_id = f"ZDK-TK-{item['id']}"
        # Map to customer IDs 1 through 10 to align with Stripe user IDs (1-10)
        customer_id = str((item['id'] % 10) + 1)
        
        # Priority and status values
        priority = random.choice(["low", "medium", "high", "critical"])
        status = random.choice(["open", "in_progress", "resolved", "closed"])
        
        # Create timestamps
        days_ago = random.randint(1, 30)
        created_date = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
        
        resolved_date = None
        if status in ["resolved", "closed"]:
            resolved_date = (datetime.utcnow() - timedelta(days=days_ago - random.randint(0, days_ago))).isoformat()
            
        ticket_data = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "title": item["name"].title(),
            "description": item["body"],
            "priority": priority,
            "status": status,
            "assigned_to": f"Support Agent {random.randint(1, 5)}",
            "created_date": created_date,
            "resolved_date": resolved_date,
            "source_system": "zendesk",
            "external_id": str(item["id"])
        }
        structured_tickets.append(ticket_data)
        
    print("Total Zendesk Tickets Extracted:", len(structured_tickets))
    
    # Save raw tickets
    output_dir = "data/raw/zendesk"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "tickets.json")
    
    with open(output_path, "w") as file:
        json.dump(structured_tickets, file, indent=4)
        
    print("Zendesk data saved successfully to", output_path)

if __name__ == "__main__":
    extract_zendesk_data()
