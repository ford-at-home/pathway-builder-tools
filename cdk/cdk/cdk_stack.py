"""Default CDK stack template.

This is the default stack template created by CDK. It's currently unused as we
use the FinancialToolsStack instead.
"""

from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from constructs import Construct


class CdkStack(Stack):
    """Default CDK stack template.

    This is the default stack template created by CDK. It's currently unused as we
    use the FinancialToolsStack instead.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Initialize the default CDK stack.

        Args:
            scope: The scope in which this stack is defined
            construct_id: The identifier for this stack
            **kwargs: Additional keyword arguments passed to the parent class
        """
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
