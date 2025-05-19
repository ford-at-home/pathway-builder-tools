# Financial Tools CLI

A command-line interface for managing financial subscriptions, products, and goals.

## Features

- 🧾 **Subscription Management**: View and manage your recurring payments
- 🧰 **Financial Products**: Discover available financial tools and products
- 🎯 **Financial Goals**: Track and manage your financial goals

## Installation

The CLI is installed as part of the `financial_tools` package. To install:

```bash
# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install financial-tools
```

## Usage

You can run the CLI in two ways:

1. Using the console script:
```bash
financial-tools
```

2. Using the Python module:
```bash
python -m financial_tools.cli
```

### Example Commands

- View subscriptions:
  ```
  > show my subscriptions
  > list my recurring payments
  ```

- View financial products:
  ```
  > show available financial products
  > what financial tools do I have access to?
  ```

- Manage goals:
  ```
  > show my financial goals
  > add a new savings goal for vacation
  > delete my car savings goal
  ```

### Navigation

- Type `exit`, `quit`, or `q` to exit the CLI
- After each command, you'll be asked if you want to continue
- Press Ctrl+C at any time to exit

## Development

### Running Tests

The CLI includes a comprehensive test suite. To run the tests:

```bash
# Run all tests
pytest

# Run CLI tests specifically
pytest financial_tools/tests/test_cli.py -v

# Run with coverage
pytest --cov=financial_tools.cli
```

### Project Structure

```
financial_tools/
├── cli/
│   ├── __init__.py
│   ├── __main__.py      # Entry point
│   ├── interface.py     # CLI implementation
│   └── README.md        # This file
├── core/                # Core functionality
│   ├── function_matcher.py
│   ├── function_executor.py
│   └── response_formatter.py
└── tests/
    └── test_cli.py      # CLI tests
```

### Adding New Features

1. Add new functionality to the core modules
2. Update the CLI interface to support new commands
3. Add tests for new functionality
4. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see the main project LICENSE file for details.
