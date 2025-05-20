"""CDK stack for financial tools infrastructure.

This module defines the AWS CDK stack that creates and configures the complete
infrastructure for the financial tools application. The stack implements a
serverless architecture using AWS Lambda and DynamoDB, with the following
components:

Infrastructure Components:
    1. DynamoDB Tables:
        - subscriptions: User subscription data
        - financial_products: Available financial products
        - financial_goals: User financial goals
        - function_catalog: Function matching catalog

    2. Lambda Functions:
        - subscriptions: Manage user subscriptions
        - products: List financial products
        - goals: Manage financial goals
        - function_matcher: Match user requests to functions
        - summarize: Generate natural language summaries

    3. IAM Permissions:
        - Lambda to DynamoDB access
        - Lambda to Bedrock access
        - Lambda to Lambda invocation

The stack is designed for development and production use, with:
    - Configurable removal policies
    - Appropriate timeouts
    - Secure IAM permissions
    - Environment variable management

Example:
    >>> from aws_cdk import App
    >>> from cdk.stacks.financial_tools_stack import FinancialToolsStack
    >>> app = App()
    >>> stack = FinancialToolsStack(app, "FinancialToolsStack")
    >>> app.synth()
"""

import os
from typing import Any

from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class FinancialToolsStack(Stack):
    """CDK stack for financial tools infrastructure.

    This stack creates and configures all AWS resources needed for the
    financial tools application. It implements a complete serverless
    architecture with proper security, scalability, and maintainability.

    Resource Configuration:
        1. DynamoDB Tables:
            - subscriptions:
                * Partition key: user_id (String)
                * Sort key: subscription_id (String)
                * Purpose: Store user subscription data
            - financial_products:
                * Partition key: product_id (String)
                * Purpose: Store available financial products
            - financial_goals:
                * Partition key: user_id (String)
                * Sort key: goal_id (String)
                * Purpose: Store user financial goals
            - function_catalog:
                * Partition key: function_id (String)
                * Purpose: Store function matching catalog

        2. Lambda Functions:
            - subscriptions:
                * Runtime: Python 3.12
                * Timeout: 30 seconds
                * Permissions: Read subscriptions table
            - products:
                * Runtime: Python 3.12
                * Timeout: 30 seconds
                * Permissions: Read products table
            - goals:
                * Runtime: Python 3.12
                * Timeout: 30 seconds
                * Permissions: Read/write goals table
            - function_matcher:
                * Runtime: Python 3.12
                * Timeout: 30 seconds
                * Permissions: Read catalog, invoke Bedrock
            - summarize:
                * Runtime: Python 3.12
                * Timeout: 60 seconds
                * Permissions: Invoke other Lambdas, invoke Bedrock

        3. IAM Permissions:
            - Lambda to DynamoDB:
                * subscriptions: Read access
                * products: Read access
                * goals: Read/write access
                * function_catalog: Read access
            - Lambda to Bedrock:
                * function_matcher: Invoke Claude model
                * summarize: Invoke Claude model
            - Lambda to Lambda:
                * summarize: Invoke other functions

    Development Features:
        - RemovalPolicy.DESTROY for easy cleanup
        - Environment variables for configuration
        - Appropriate timeouts for operations
        - Secure IAM permissions

    Example:
        >>> from aws_cdk import App
        >>> app = App()
        >>> stack = FinancialToolsStack(app, "FinancialToolsStack")
        >>> # Deploy the stack
        >>> app.synth()
    """

    def __init__(self, scope: Construct, id: str, **kwargs: Any) -> None:
        """Initialize the financial tools stack.

        This constructor creates and configures all AWS resources needed for
        the financial tools application. It sets up:
            1. DynamoDB tables with appropriate keys and policies
            2. Lambda functions with proper runtime and permissions
            3. IAM roles and policies for secure access
            4. Environment variables for configuration

        The stack is designed to be deployed in a single operation, with all
        resources properly configured and connected.

        Args:
            scope: The scope in which this stack is defined. This is typically
                an App instance from aws_cdk.App.
            id: The identifier for this stack. This should be unique within
                the scope and is used to identify the stack in CloudFormation.
            **kwargs: Additional keyword arguments passed to the parent class.
                These can include:
                - env: The environment to deploy to
                - description: Stack description
                - tags: Resource tags

        Example:
            >>> from aws_cdk import App
            >>> app = App()
            >>> stack = FinancialToolsStack(
            ...     app,
            ...     "FinancialToolsStack",
            ...     description="Financial tools infrastructure",
            ...     env={"region": "us-west-2"}
            ... )
        """
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB tables
        subscriptions_table = ddb.Table(
            self,
            "SubscriptionsTable",
            table_name="subscriptions",
            partition_key={"name": "user_id", "type": ddb.AttributeType.STRING},
            sort_key={"name": "subscription_id", "type": ddb.AttributeType.STRING},
            # Makes it easier to clean up during development
            removal_policy=RemovalPolicy.DESTROY,
        )

        products_table = ddb.Table(
            self,
            "FinancialProductsTable",
            table_name="financial_products",
            partition_key={"name": "product_id", "type": ddb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY,
        )

        goals_table = ddb.Table(
            self,
            "FinancialGoalsTable",
            table_name="financial_goals",
            partition_key={"name": "user_id", "type": ddb.AttributeType.STRING},
            sort_key={"name": "goal_id", "type": ddb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY,
        )

        lambda_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda")

        # Create Lambda functions
        subscriptions_fn = _lambda.Function(
            self,
            "GetSubscriptionsFunction",
            function_name="subscriptions",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="subscriptions.handler",
            code=_lambda.Code.from_asset(lambda_dir),
            environment={"TABLE_NAME": subscriptions_table.table_name},
            timeout=Duration.seconds(30),
        )
        subscriptions_table.grant_read_data(subscriptions_fn)

        products_fn = _lambda.Function(
            self,
            "GetFinancialProductsFunction",
            function_name="products",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="products.handler",
            code=_lambda.Code.from_asset(lambda_dir),
            environment={"TABLE_NAME": products_table.table_name},
            timeout=Duration.seconds(30),
        )
        products_table.grant_read_data(products_fn)

        goals_fn = _lambda.Function(
            self,
            "GoalsFunction",
            function_name="goals",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="goals.handler",
            code=_lambda.Code.from_asset(lambda_dir),
            environment={"TABLE_NAME": goals_table.table_name},
            timeout=Duration.seconds(30),
        )
        goals_table.grant_read_write_data(goals_fn)

        # Create function catalog table
        function_catalog_table = ddb.Table(
            self,
            "FunctionCatalogTable",
            table_name="function_catalog",
            partition_key={"name": "function_id", "type": ddb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create function matcher Lambda
        function_matcher_fn = _lambda.Function(
            self,
            "FunctionMatcherFunction",
            function_name="function_matcher",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="function_matcher.handler",
            code=_lambda.Code.from_asset(lambda_dir),
            environment={"TABLE_NAME": function_catalog_table.table_name},
            timeout=Duration.seconds(30),
        )

        # Create summarize Lambda function
        summarize_fn = _lambda.Function(
            self,
            "SummarizeFunction",
            function_name="summarize",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="summarize.handler",
            code=_lambda.Code.from_asset(lambda_dir),
            timeout=Duration.seconds(60),  # Longer timeout for Bedrock calls
        )

        # Grant Bedrock permissions to both functions
        for fn in [function_matcher_fn, summarize_fn]:
            fn.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["bedrock:InvokeModel"],
                    resources=[
                        "arn:aws:bedrock:*::foundation-model/"
                        "anthropic.claude-3-sonnet-20240229-v1:0"
                    ],
                )
            )

        # Grant Lambda invoke permissions to summarize function
        summarize_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[
                    subscriptions_fn.function_arn,
                    products_fn.function_arn,
                    goals_fn.function_arn,
                ],
            )
        )

        function_catalog_table.grant_read_data(function_matcher_fn)
