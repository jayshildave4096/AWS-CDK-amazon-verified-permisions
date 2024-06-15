#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
import click
from stack.api_stages_lambda_stack import ApiStagesLambdaStack
from stack.avp_stack import AVPStack


app = cdk.App()
AVPStack(
    app, "AVPStack", env=cdk.Environment(account="465283423899", region="us-east-1")
)
ApiStagesLambdaStack(
    app,
    "ApiStagesLambdaStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    env=cdk.Environment(account="465283423899", region="us-east-1"),
)

app.synth()
