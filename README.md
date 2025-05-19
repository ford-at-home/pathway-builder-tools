# pathway-builder-tools
Tools for agents to use in building pathways to financial freedom.

This project uses AWS CDK (Python) to deploy a suite of Lambda functions and their associated DynamoDB tables, providing a comprehensive financial management backend. The system includes:

- **Subscriptions Manager** — Handles recurring user subscriptions
- **Financial Products Manager** — Returns a list of available financial products
- **Financial Goals Manager** — Allows users to get, put, and delete financial goals
- **Function Catalog & Matcher** — Uses Amazon Bedrock (Claude 3) to intelligently route user requests to the appropriate function

## Directory Structure

```
pathway-builder-tools/
├── cdk/                      # CDK application code
│   ├── app.py               # CDK app entry point
│   ├── stacks/              # CDK stack definitions
│   │   └── financial_tools_stack.py
│   ├── lambda/              # Lambda function handlers
│   │   ├── subscriptions.py
│   │   ├── products.py
│   │   ├── goals.py
│   │   └── function_matcher.py
│   ├── cdk/                 # Default CDK template (unused)
│   │   └── cdk_stack.py
│   └── tests/               # CDK infrastructure tests
│       └── unit/
│           └── test_cdk_stack.py
├── scripts/                  # Utility scripts
│   ├── test_functions.py    # Test function matcher and execution
│   ├── seed_subscriptions.py
│   ├── seed_products.py
│   ├── seed_goals.py
│   └── seed_function_catalog.py
├── tests/                    # Application tests
│   ├── conftest.py          # Test fixtures and configuration
│   └── test_subscriptions.py
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── requirements.txt          # Python dependencies
├── Makefile                 # Build and deployment commands
└── README.md                # This file
```

## Prerequisites

- AWS CLI configured
- Python 3.12
- AWS CDK v2
- `boto3` installed for seeding scripts
- AWS Bedrock access (for function matching)

## Setup & Deployment

The easiest way to deploy is using the Makefile:

```bash
make setup  # Creates venv, installs deps, deploys stack, and seeds data
```

This will:
1. Create a Python virtual environment
2. Install all dependencies
3. Bootstrap the CDK environment
4. Deploy the stack
5. Seed all DynamoDB tables

Other useful make commands:
```bash
make deploy   # Deploy the CDK stack
make destroy  # Destroy the CDK stack
make seed     # Seed the DynamoDB tables
make clean    # Clean up generated files
make test-function prompt="Show my subscriptions"  # Test function matcher
```

## Lambda Function Handlers

* `subscriptions.handler`: Queries subscriptions by `user_id`
* `products.handler`: Scans all available products
* `goals.handler`: Supports `get`, `put`, and `delete` actions for financial goals
* `function_matcher.handler`: Uses Amazon Bedrock (Claude 3) to match user requests to the most appropriate function

## Function Catalog

The function catalog is a DynamoDB table that stores metadata about each available function:

```json
{
    "function_id": "get_subscriptions",
    "title": "Get User Subscriptions",
    "tool_title": "Subscription Manager",
    "description": "Retrieves all active subscriptions for a user...",
    "category": "subscriptions",
    "example_prompts": [
        "Show me my subscriptions",
        "What subscriptions do I have?",
        "List all my monthly subscriptions"
    ]
}
```

The function matcher uses this catalog to:
1. Take a user's natural language request
2. Use Claude 3 to analyze the request
3. Match it to the most appropriate function
4. Return the function's details for execution

## Testing

The project includes comprehensive testing:

1. **Unit Tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=cdk

   # Run specific test file
   pytest tests/test_subscriptions.py
   ```

2. **Function Testing**
   ```bash
   # Test function matcher with a prompt
   make test-function prompt="Show my subscriptions"

   # Test with specific user ID
   make test-function prompt="Show my subscriptions" user_id="user123"

   # Test without execution
   make test-function prompt="Show my subscriptions" skip=true
   ```

3. **Infrastructure Tests**
   ```bash
   # Synthesize CloudFormation template
   make synth
   ```

## Development Workflow

1. Create a new branch for your feature
2. Install pre-commit hooks (they'll run automatically on commit)
3. Write tests for your feature
4. Implement the feature
5. Run tests locally
6. Create a pull request

## Code Quality

The project uses several tools to maintain code quality:

- **Pre-commit Hooks**
  - black: Code formatting
  - isort: Import sorting
  - flake8: Linting
  - mypy: Type checking

- **Testing**
  - pytest: Unit and integration tests
  - moto: AWS service mocking
  - pytest-cov: Test coverage

## Security Notes

- All Lambda functions use IAM roles with least privilege
- Function matcher has specific permissions for Bedrock model invocation
- DynamoDB tables use simple names but are protected by IAM policies
- No sensitive data is stored in the function catalog

## For Agent Developers

This infrastructure provides a foundation for building agentic financial tools. Here's what you need to know:

### Available Functions

Each function in our catalog is designed to be agent-friendly:

1. **Subscription Management**
   - Function ID: `get_subscriptions`
   - Input: `{"user_id": "string"}`
   - Output: List of active subscriptions with amounts and frequencies
   - Use Case: Help users understand their recurring expenses

2. **Financial Products**
   - Function ID: `get_products`
   - Input: None required
   - Output: List of available financial products with eligibility criteria
   - Use Case: Match users with appropriate financial products based on their needs

3. **Financial Goals**
   - Function IDs: `get_goals`, `put_goal`, `delete_goal`
   - Input: Varies by operation (see example prompts in catalog)
   - Output: Goal details or operation status
   - Use Case: Help users set and track financial goals

### Function Matching

The function matcher (`function_matcher.handler`) is your entry point for natural language processing:

```python
# Example request to function matcher
{
    "prompt": "Show me my monthly subscriptions",
    "user_id": "user123"  # Optional, for context
}

# Example response
{
    "function_id": "get_subscriptions",
    "title": "Get User Subscriptions",
    "description": "Retrieves all active subscriptions...",
    "parameters": {
        "user_id": "user123"
    }
}
```

### Best Practices for Agent Implementation

1. **Function Discovery**
   - Use the function matcher as your first step
   - The catalog includes example prompts to help train your agent
   - Each function has a clear category and description

2. **Error Handling**
   - All functions return standard HTTP status codes
   - Check for `errorMessage` in responses
   - Handle missing user_id or invalid parameters gracefully

3. **Data Types**
   - All monetary values are stored as Decimals
   - Dates are in ISO 8601 format
   - IDs are strings

4. **Security Considerations**
   - Always validate user input
   - Use the provided IAM roles
   - Don't store sensitive data in the function catalog
   - Handle errors gracefully and log appropriately

5. **Extending the System**
   - New functions can be added to the catalog
   - Update the seeding script with new function metadata
   - Follow the existing pattern for function definitions

### Example Agent Flow

```python
# Pseudocode for agent implementation
async def handle_user_request(user_prompt: str, user_id: str):
    # 1. Match the request to a function
    match_response = await call_function_matcher({
        "prompt": user_prompt,
        "user_id": user_id
    })

    # 2. Execute the matched function
    function_id = match_response["function_id"]
    parameters = match_response["parameters"]

    # 3. Call the appropriate function
    result = await call_function(function_id, parameters)

    # 4. Format the response for the user
    return format_response(result, match_response["title"])
```

### Testing Your Agent

1. Use the example prompts from the function catalog
2. Test with various phrasings of the same request
3. Verify error handling with invalid inputs
4. Test the full flow from natural language to function execution

### Getting Started

1. Deploy this infrastructure using `make setup`
2. Review the function catalog in DynamoDB
3. Implement your agent to use the function matcher
4. Add your agent's Lambda function to the stack
5. Update the function catalog with any new functions

Remember: This infrastructure is designed to be extended. Feel free to add new functions to the catalog and update the function matcher's training data as needed.

# Pathway Builder Tools

This repository contains a suite of tools (and a test script) for interacting with AWS Lambda functions (e.g. a "function matcher" and functions for subscriptions, products, and financial goals) via natural language prompts.

## Overview

- **scripts/test_functions.py** is a Python script that:
  - Calls a "function matcher" Lambda (using boto3) to recommend a function (and parameters) based on a natural language prompt.
  - (If a "body" field is present in the response, it is parsed (and flattened) so that the function_id, parameters, title, and description are returned at the top level.)
  - Executes the recommended (or a mapped) function (for example, "manage_goals" (or "Manage Financial Goals") is mapped to "get_goals" (with action="get") for read actions) via the AWS Lambda client.
  - Formats the response (for subscriptions, products, and goals) so that if a key (e.g. "subscriptions", "products", "goals") is present, it is used; otherwise, it falls back to "Items".
  - Displays a user-friendly output (or a raw JSON dump for unknown functions).

## Prerequisites

- Python 3.6 (or later) and pip (or a virtual environment).
- AWS credentials (and boto3) configured (e.g. via ~/.aws/credentials or environment variables).
- AWS Lambda functions (e.g. "function_matcher", "subscriptions", "products", "goals") deployed (and configured) in your AWS account.

## Installation

Clone the repo (or download the scripts) and install (or activate) your Python environment. (No extra dependencies are required if boto3 is installed.)

## Usage

Run the test script (e.g. from the repo root) as follows:

```bash
python3 scripts/test_functions.py "your prompt" [--user-id <user_id>] [--skip-execution]
```

### Examples

- **Show subscriptions (for a test user):**

  ```bash
  python3 scripts/test_functions.py "Show me all my monthly subscriptions"
  ```

  Expected output (if subscriptions exist):

  ```
  🤖 Processing your request...

  📋 Function Matcher Recommendation:
  Function: Get User Subscriptions
  Description: Retrieves all active subscriptions for a user, including subscription name, amount, frequency, and category.
  Parameters: {}

  ⚡ Executing function...

  🐞 Raw Lambda Response:
  { "subscriptions": [ { "user_id": "test_user", "subscription_id": "sub-001", "name": "Spotify", "amount": 9.99, "frequency": "monthly", "category": "Entertainment", "start_date": "2024-11-01" }, { "user_id": "test_user", "subscription_id": "sub-002", "name": "Netflix", "amount": 15.99, "frequency": "monthly", "category": "Entertainment", "start_date": "2024-10-15" } ] }

  📊 Result:

  Subscriptions:
  - Spotify: $9.99 (monthly)
  - Netflix: $15.99 (monthly)
  ```

- **Show available products (for a test user):**

  ```bash
  python3 scripts/test_functions.py "Show me all available products"
  ```

  Expected output (if products exist):

  ```
  🤖 Processing your request...

  📋 Function Matcher Recommendation:
  Function: Get Financial Products
  Description: Retrieves available financial products (e.g. loans) with details (interest rates, terms, amount ranges).
  Parameters: {}

  ⚡ Executing function...

  🐞 Raw Lambda Response:
  { "products": [ { "product_id": "prod-001", "name": "Mortgage", "description": "30-year fixed rate mortgage", "min_amount": 50000, "max_amount": 500000, "interest_rate": 6.5, "term_years": 30, "type": "loan" }, { "product_id": "prod-002", "name": "Auto Loan", "description": "5-year auto loan", "min_amount": 10000, "max_amount": 100000, "interest_rate": 5.5, "term_years": 5, "type": "loan" } ] }

  📊 Result:

  Available Products:
  - Mortgage: 30-year fixed rate mortgage
    Amount Range: $50000 - $500000
  - Auto Loan: 5-year auto loan
    Amount Range: $10000 - $100000
  ```

- **Show financial goals (for a test user):**

  (Note that the function matcher returns "Manage Financial Goals" (or "manage_goals"), which is mapped (in the script) to "get_goals" (with action="get") for read actions.)

  ```bash
  python3 scripts/test_functions.py "Show me my financial goals"
  ```

  Expected output (if goals exist):

  ```
  🤖 Processing your request...

  📋 Function Matcher Recommendation:
  Function: Manage Financial Goals
  Description: Create, read, update, and delete financial goals. Track progress towards savings targets, emergency funds, and other financial objectives.
  Parameters: {}

  ⚡ Executing function...

  🐞 Raw Lambda Response:
  { "goals": [ { "goal_id": "goal-001", "user_id": "test_user", "name": "Vacation Fund", "current_amount": 1200, "target_amount": 3000, "category": "Travel", "due_date": "2024-12-31" }, { "goal_id": "goal-002", "user_id": "test_user", "name": "Emergency Fund", "current_amount": 3500, "target_amount": 10000, "category": "Savings", "due_date": "2024-06-30" } ] }

  📊 Result:

  Financial Goals:
  - Vacation Fund: $1200 / $3000 (Due: 2024-12-31)
  - Emergency Fund: $3500 / $10000 (Due: 2024-06-30)
  ```

- **Skip execution (only show the function matcher recommendation):**

  ```bash
  python3 scripts/test_functions.py "your prompt" --skip-execution
  ```

- **Specify a user (e.g. "user-123"):**

  ```bash
  python3 scripts/test_functions.py "your prompt" --user-id user-123
  ```

 (Adjust the prompt and expected output as needed.)

## Notes

- The script (scripts/test_functions.py) is intended for testing (or demo) purposes. (It is not intended for production use.)
- Ensure that your AWS Lambda functions (e.g. "function_matcher", "subscriptions", "products", "goals") are deployed (and configured) in your AWS account (and that your AWS credentials (and boto3) are set up) so that the script can invoke them.
- (If you'd like to test "put" or "delete" goals (or other flows), please adjust the prompt (and parameters) accordingly.)
