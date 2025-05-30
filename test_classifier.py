from app.agents.classifier_agent import classify_input

# Test with an email-like input
email_test = """
From: john.doe@example.com
Subject: Urgent Quote Request
Dear Sales Team,
We need a quote for 100 units of your product ABC-123.
Best regards,
John
"""

# Test with a JSON-like input
json_test = """
{
  "order_id": "ORD-123",
  "customer": {
    "name": "Acme Corp",
    "id": "CUST-456"
  },
  "items": [
    {
      "product_id": "ABC-123",
      "quantity": 100,
      "unit_price": 49.99
    }
  ],
  "total_amount": 4999.00
}
"""

print("Testing email classification:")
print(classify_input(email_test))
print("\nTesting JSON classification:")
print(classify_input(json_test))
