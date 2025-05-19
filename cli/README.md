# Financial Assistant CLI

A command-line interface for interacting with the Pathway Builder Tools financial management system. This CLI provides a friendly interface to manage subscriptions, explore financial products, and track financial goals.

## Features

- 🧾 View and manage recurring subscriptions
- 🧰 Discover available financial products
- 🎯 Track and manage financial goals
- 🤖 AI-powered request understanding
- 📝 Summarized responses for better readability

## Prerequisites

- Python 3.8 or higher
- AWS credentials configured
- Access to the required Lambda functions:
  - `tool_picker`
  - `subscriptions_tool`
  - `financial_products_tool`
  - `financial_goals_tool`
  - `summarizer`

## Installation

1. Navigate to the CLI directory:
   ```bash
   cd cli
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI:
```bash
python main.py
```

Example interactions:
```
👋 Hi, I'm your CLI financial tool assistant.

I can help you with 3 things:
  1. 🧾 Subscriptions – "Show me my recurring payments"
  2. 🧰 Financial Products – "List some financial tools I could use"
  3. 🎯 Financial Goals – "Add a new goal to save for vacation"

How can I help today?
> show me my subscriptions

You have 2 active subscriptions:
- Netflix: $15.99/month
- Spotify: $9.99/month

Would you like to ask something else? (y/n):
```

## Development

### Running Tests

```bash
pytest
```

### Project Structure

- `main.py`: Main CLI application and core classes
- `tests/`: Test suite
- `requirements.txt`: Project dependencies

### Key Components

1. `LambdaClient`: Handles all AWS Lambda function invocations
2. `ResponseFormatter`: Formats and displays responses
3. `FinancialAssistantCLI`: Main CLI interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
