#!/usr/bin/env python3
"""CDK application entry point.

This module initializes and synthesizes the CDK app, creating the
financial tools infrastructure stack.
"""
import aws_cdk as cdk
from stacks.financial_tools_stack import FinancialToolsStack

app = cdk.App()
FinancialToolsStack(app, "FinancialToolsStack")
app.synth()
