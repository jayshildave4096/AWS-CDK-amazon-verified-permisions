from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_iam as iam,
    Aws, CfnOutput,
    aws_cognito as cognito,
    aws_verifiedpermissions as verifiedpermissions
    
)
from constructs import Construct
import json

class ApiStagesLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define AWS Lambda function and aliases
        function = _lambda.Function(self, "LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda-handler.handler",
            code=_lambda.Code.from_asset("lambda")
        )


        userpool = cognito.UserPool(self, "Demo-User-Pool-2604", self_sign_up_enabled=True)
        userpool_client = userpool.add_client("democlient", auth_flows=cognito.AuthFlow(
            user_password=True,
            user_srp=True,
            admin_user_password=True
        ))

        # Define the REST API
        api = apigw.RestApi(self, "DeploymentStagesAPI",
            rest_api_name="MultiStageApi",
            deploy=False
        )

        # Define GET method for /stage_info
        stage_info_resource = api.root.add_resource("stage_info")
        stage_info_get_method = stage_info_resource.add_method("GET",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )
        
        # GET /photo
        photo_resource = api.root.add_resource("photo")
        photo_get_method = photo_resource.add_method("GET",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )

        # POST /photo
        photo_post_method = photo_resource.add_method("POST",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )

        # PATCH /photo
        photo_patch_method = photo_resource.add_method("PATCH",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )

        # DELETE /photo
        photo_delete_method = photo_resource.add_method("DELETE",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )

        # GET /friends
        friends_resource = api.root.add_resource("friends")
        friends_get_method = friends_resource.add_method("GET",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )


        # POST /friend
        friend_resource = api.root.add_resource("friend")
        friend_post_method = friend_resource.add_method("POST",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )


        # DELETE /friend
        friend_delete_method = friend_resource.add_method("DELETE",
            authorization_type=apigw.AuthorizationType.IAM,
            integration=apigw.AwsIntegration(
                service="lambda",
                region=Aws.REGION,
                proxy=True,
                path=f"2015-03-31/functions/{function.function_arn}/invocations"
            )
        )

        prod_deployment = apigw.Deployment(self, "ProdApiDeployment", api=api)    
        prod_stage = apigw.Stage(self, "ProdApiStage",
            deployment=prod_deployment,
            stage_name="prod",
        )
        
        function.grant_invoke(iam.ServicePrincipal('apigateway.amazonaws.com'))


        # Define Test specific resources 
        # TODO: Move this conftest or test file
        # test_alias = _lambda.Alias(self, "TestAlias",
        #     alias_name="test",
        #     version=version
        # )

        # test_deployment = apigw.Deployment(self, "TestApiDeployment", api=api)    
        # test_stage = apigw.Stage(self, "TestApiStage",
        #     deployment=test_deployment,
        #     stage_name="test",
        #     variables={
        #         "lambdaAlias": test_alias.alias_name
        #     }
        # )

        # test_alias.add_permission("TestStageInvokeTestAliasPermission",
        #     principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
        #     action="lambda:InvokeFunction",
        #     source_arn=api.arn_for_execute_api(
        #         method=stage_info_get_method.http_method,
        #         path=stage_info_resource.path,
        #         stage=test_stage.stage_name
        #     )
        # )

        # Define outputs
        CfnOutput(self, "ApiHostUrl", 
            value=f"{api.rest_api_id}.execute-api.{Aws.REGION}.amazonaws.com",
            description="API Host URL"
        )
        CfnOutput(self, "UserPoolId",
            value=f"{userpool.user_pool_id}",
            description="User Pool ID"
        )
        CfnOutput(self, "UserPoolClientId",
            value=f"{userpool_client.user_pool_client_id}",
            description="UserPool Client ID"
        )
