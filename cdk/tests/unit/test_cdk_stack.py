"""Unit tests for the default CDK stack.

This module contains example tests for the default CDK stack. These tests are
currently unused as we use the FinancialToolsStack instead.
"""

import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.cdk_stack import CdkStack


def test_sqs_queue_created() -> None:
    """Test that an SQS queue is created with the correct properties.

    This is an example test that is currently commented out as we don't use
    the default CDK stack.
    """
    app = core.App()
    stack = CdkStack(app, "cdk")
    template = assertions.Template.from_stack(stack)

    # Example test for SQS queue properties
    # template.has_resource_properties("AWS::SQS::Queue", {
    #     "VisibilityTimeout": 300
    # })
