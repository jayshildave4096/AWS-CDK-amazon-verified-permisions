from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_iam as iam,
    Aws,
    CfnOutput,
    aws_cognito as cognito,
    aws_verifiedpermissions as verifiedpermissions,
    BundlingOptions,
    Duration,
)
from constructs import Construct
import os


class ApiStagesLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define AWS Lambda function and aliases
        function = _lambda.Function(
            self,
            "LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda-handler.handler",
            code=_lambda.Code.from_asset("lambda"),
        )

        # Define AWS Lambda function and aliases
        auth_function = _lambda.Function(
            self,
            "AuthLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="auth-lambda-handler.handler",
            initial_policy=[
                iam.PolicyStatement(
                    actions=["verifiedpermissions:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            ],
            environment={"POLICY_STORE_ID": os.environ.get("POLICY_STORE_ID")},
            code=_lambda.Code.from_asset(
                "auth_lambda",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                ),
            ),
        )

        # TO CREATE USERPOOL VIA CLOUD FORMATION
        # userpool = cognito.UserPool(self, "Demo-User-Pool-2604", self_sign_up_enabled=True)
        # userpool_client = userpool.add_client("democlient", auth_flows=cognito.AuthFlow(
        #     user_password=True,
        #     user_srp=True,
        #     admin_user_password=True
        # ))

        # Define the REST API
        api = apigw.RestApi(self, "TestApiAPI", rest_api_name="TestApi", deploy=False)

        # Define GET method for /stage_info
        auth_info_resource = api.root.add_resource("auth")
        auth_info_get_method = auth_info_resource.add_method(
            "GET",
            authorization_type=apigw.AuthorizationType.NONE,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{auth_function.function_arn}/invocations",
            ),
        )

        authorizer = apigw.RequestAuthorizer(
            self,
            "TestAuthorizer",
            handler=auth_function,
            identity_sources=[apigw.IdentitySource.header("Auth-Token")],
            results_cache_ttl=Duration.seconds(0),
        )

        # GET /photo
        photo_resource = api.root.add_resource("photo")
        photo_get_method = photo_resource.add_method(
            "GET",
            authorization_type=apigw.AuthorizationType.CUSTOM,
            authorizer=authorizer,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations",
            ),
        )

        # POST /photo
        photo_post_method = photo_resource.add_method(
            "POST",
            authorization_type=apigw.AuthorizationType.CUSTOM,
            authorizer=authorizer,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations",
            ),
        )

        # DELETE /photo
        photo_delete_method = photo_resource.add_method(
            "DELETE",
            authorization_type=apigw.AuthorizationType.CUSTOM,
            authorizer=authorizer,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations",
            ),
        )

        prod_deployment = apigw.Deployment(self, "ProdApiDeployment", api=api)
        prod_stage = apigw.Stage(
            self,
            "ProdApiStage",
            deployment=prod_deployment,
            stage_name="prod",
        )

        function.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
        auth_function.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))

        # Define outputs
        CfnOutput(
            self,
            "ApiHostUrl",
            value=f"{api.rest_api_id}.execute-api.{Aws.REGION}.amazonaws.com",
            description="API Host URL",
        )

        # TO OUTPUT USERPOOL ID AND CLIENT ID
        # CfnOutput(self, "UserPoolId",
        #     value=f"{userpool.user_pool_id}",
        #     description="User Pool ID"
        # )
        # CfnOutput(self, "UserPoolClientId",
        #     value=f"{userpool_client.user_pool_client_id}",
        #     description="UserPool Client ID"
        # )
