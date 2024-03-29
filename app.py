#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
import click
from stack.api_stages_lambda_stack import ApiStagesLambdaStack


client = boto3.client('cognito-idp')
def create_user(username,password):
    

    # initial sign up
   
    client_id = os.environ.get('CLIENT_ID')
    resp = client.sign_up(
        ClientId= client_id,
        Username= username,
        Password= password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': 'test@test.com'
            },
        ]
    )

def confirm_signup(username):
    resp = client.admin_confirm_sign_up(
        UserPoolId=os.environ.get('USER_POOL_ID'),
        Username=username
    )
    print(resp)

def login(username,password):
    resp = client.admin_initiate_auth(
        UserPoolId=os.environ.get('USER_POOL_ID'),
        ClientId=os.environ.get('CLIENT_ID'),
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )
    # TODO: return ID Token
    print(resp)

    


@click.command()
@click.option('--endpoint',  help='API Endpoint')
@click.option('--username',  help='Username')
@click.option('--password',  help='password')
@click.option('--c',type=bool,  help='option')
def main(endpoint, username,password,c):
    response = client.list_user_pools(
        MaxResults=10
    )
    user_pool_id = response['UserPools'][0]['Id']
    os.environ['USER_POOL_ID']=user_pool_id

    response = client.list_user_pool_clients(
       UserPoolId=user_pool_id
    )

    client_id = response['UserPoolClients'][0]['ClientId']
    os.environ['CLIENT_ID']=client_id
    print(create_user)
    if c:
        create_user(username,password)
        confirm_signup(username)
        login(username,password)
    print("Done")
    print(user_pool_id)
    print(client_id)
    #To make actual requesst here

if __name__ == '__main__':
    main()