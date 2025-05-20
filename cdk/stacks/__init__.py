"""CDK stack definitions for the financial tools application.

This package contains the AWS CDK stack definitions that create and configure
the complete infrastructure for the financial tools application. The stacks
implement a serverless architecture using AWS Lambda and DynamoDB.

Package Contents:
    - FinancialToolsStack: Main stack that creates all infrastructure
        * DynamoDB tables for data storage
        * Lambda functions for business logic
        * IAM roles and policies for security
        * Environment variables for configuration

The package is designed to be used with AWS CDK to deploy the complete
infrastructure in a single operation. It provides a modular and maintainable
way to manage the application's cloud resources.

Example:
    >>> from aws_cdk import App
    >>> from cdk.stacks import FinancialToolsStack
    >>> app = App()
    >>> stack = FinancialToolsStack(app, "FinancialToolsStack")
    >>> app.synth()
"""

from .financial_tools_stack import FinancialToolsStack

__all__ = ["FinancialToolsStack"]
