from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("financial_products")

products = [
    {
        "product_id": "prod-001",
        "name": "Mortgage",
        "type": "loan",
        "description": "30-year fixed rate mortgage",
        "min_amount": Decimal("50000"),
        "max_amount": Decimal("500000"),
        "interest_rate": Decimal("6.5"),
        "term_years": 30,
    },
    {
        "product_id": "prod-002",
        "name": "Auto Loan",
        "type": "loan",
        "description": "5-year auto loan",
        "min_amount": Decimal("10000"),
        "max_amount": Decimal("100000"),
        "interest_rate": Decimal("5.5"),
        "term_years": 5,
    },
]

for item in products:
    table.put_item(Item=item)
