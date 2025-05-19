"""CDK stack for financial tools infrastructure.

This module defines the AWS CDK stack that creates the infrastructure for the
financial tools application, including DynamoDB tables and Lambda functions.
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

    This stack creates:
    - DynamoDB tables for subscriptions, products, goals, and function catalog
    - Lambda functions for managing subscriptions, products, goals, and function matching
    - IAM permissions for Lambda functions to access DynamoDB and Bedrock
    """

    def __init__(self, scope: Construct, id: str, **kwargs: Any) -> None:
        """Initialize the financial tools stack.

        Args:
            scope: The scope in which this stack is defined
            id: The identifier for this stack
            **kwargs: Additional keyword arguments passed to the parent class
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
