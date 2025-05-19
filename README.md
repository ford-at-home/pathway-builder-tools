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

## Components

### CLI Interface

The project includes a command-line interface for interacting with the financial tools system. See [CLI Documentation](financial_tools/cli/README.md) for details.

Features:
- 🧾 Subscription management
- 🧰 Financial product discovery
- 🎯 Goal tracking and management

Quick start:
```bash
# Install the package
pip install -e .

# Run the CLI
financial-tools
```

### Lambda Functions

The system includes several AWS Lambda functions for processing requests:

- `function_matcher`: Matches natural language requests to appropriate functions
- `subscriptions`: Manages subscription data
- `products`: Handles financial product information
- `goals`: Manages financial goals
