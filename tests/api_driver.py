import json
import requests
import argparse
import boto3
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

RESOURCE = "fruits"

def test_prod_api(apiurl, region):
    stage = "prod"
    auth = BotoAWSRequestsAuth(aws_host=apiurl, aws_region=region, aws_service='execute-api')
    res = requests.get(f"https://{apiurl}/{stage}/{RESOURCE}", timeout=2, auth=auth,headers={
        "ContentType":"application/json"
    })
    res_body = json.loads(res.text)

    assert res.status_code == 200
    assert res_body['apiStage'] == stage

def test_user():
    client = boto3.client('cognito-idp')

    # # initial sign up
    # response = client.list_user_pool_clients(
    # UserPoolId='us-east-1_JKSV2ZSCX')
    # print(response)
    # resp = client.sign_up(
    #     ClientId= "55ak2dlghskdf5gjvnm9ilnsr2",
    #     Username= "aishwarya",
    #     Password= "Abc@123456",
    #     UserAttributes=[
    #         {
    #             'Name': 'email',
    #             'Value': 'test@test.com'
    #         },
    #     ]
    # )
    # print(resp)
    # #without email verification confirmation
    # resp = client.admin_confirm_sign_up(
    #     UserPoolId='us-east-1_JKSV2ZSCX',
    #     Username='aishwarya'
    # )

    print("User successfully created.")
    
    resp = client.admin_initiate_auth(
        UserPoolId='us-east-1_JKSV2ZSCX',
        ClientId='55ak2dlghskdf5gjvnm9ilnsr2',
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            "USERNAME": 'aishwarya',
            "PASSWORD": 'Abc@123456'
        }
    )

    print("Log in success")
    print("Access token:", resp['AuthenticationResult']['AccessToken'])
    print("ID token:", resp['AuthenticationResult']['IdToken'])

# def test_dev_api(apiurl, region):
#     stage = "dev"
#     auth = BotoAWSRequestsAuth(aws_host=apiurl, aws_region=region, aws_service='execute-api')
#     res = requests.get(f"https://{apiurl}/{stage}/{RESOURCE}", timeout=2, auth=auth)
#     res_body = json.loads(res.text)

#     assert res.status_code == 200
#     assert res_body['apiStage'] == stage
#     assert res_body['lambdaAlias'] == stage

# def test_test_api(apiurl, region):
#     stage = "test"
#     auth = BotoAWSRequestsAuth(aws_host=apiurl, aws_region=region, aws_service='execute-api')
#     res = requests.get(f"https://{apiurl}/{stage}/{RESOURCE}", timeout=2, auth=auth)
#     res_body = json.loads(res.text)

#     assert res.status_code == 200
#     assert res_body['apiStage'] == stage
#     assert res_body['lambdaAlias'] == stage

