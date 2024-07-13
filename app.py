#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
import click
from stack.api_stages_lambda_stack import ApiStagesLambdaStack
from jwt import JWT
from jwt.exceptions import JWTDecodeError
import requests


def decode_token(token: str):
    try:
        jwt_ = JWT()
        return jwt_.decode(token, algorithms=["RS256"], do_verify=False)
    except JWTDecodeError as e:
        print("token expired")


client = boto3.client("cognito-idp")


def create_user(username, password, cid):
    # initial sign up
    resp = client.sign_up(
        ClientId=cid,
        Username=username,
        Password=password,
        UserAttributes=[
            {"Name": "email", "Value": "test@test.com"},
        ],
    )


def confirm_signup(username, uid):
    resp = client.admin_confirm_sign_up(UserPoolId=uid, Username=username)
    print(resp)


def login(username, password, uid, cid):
    resp = client.admin_initiate_auth(
        UserPoolId=uid,
        ClientId=cid,
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )
    return resp["AuthenticationResult"]["IdToken"]


@click.command()
@click.option("--endpoint", help="API Endpoint")
@click.option("--username", help="Username")
@click.option("--password", help="password")
@click.option("--uid", help="userpool id")
@click.option("--cid", help="client id")
def main(endpoint, username, password, uid, cid):
    # FUNCTIONS TO ADD USERS TO THE USERPOOL
    # create_user(username, password,cid)
    # confirm_signup(username,uid)

    # FETCH TOKEN FROM COGNITO
    token = login(username, password, uid, cid)

    response = requests.get(
        f"{endpoint}/prod/photo",
        params={"userpool_id": uid, "client_id": cid, "resource": "sunset.jpg"},
        headers={"Auth-Token": token},
    ).json()

    response1 = requests.post(
        f"{endpoint}/prod/photo",
        params={"userpool_id": uid, "client_id": cid, "resource": "sunset.jpg"},
        headers={"Auth-Token": token},
    ).json()

    response2 = requests.delete(
        f"{endpoint}/prod/photo",
        params={"userpool_id": uid, "client_id": cid, "resource": "sunset.jpg"},
        headers={"Auth-Token": token},
    ).json()

    print("GET:", response)
    print("POST", response1)
    print("DELETE", response2)


if __name__ == "__main__":
    main()
