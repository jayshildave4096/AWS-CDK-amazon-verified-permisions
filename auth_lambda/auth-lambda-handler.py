import boto3
import json
import time
import os
from typing import Dict, List, Any
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from dataclasses import asdict, dataclass

region = "us-east-1"
avp_client = boto3.client("verifiedpermissions")
POLICY_STORE_ID = os.environ.get("POLICY_STORE_ID")


@dataclass
class Identifier:
    entityId: str
    entityType: str


action = {"GET": "ReadPhotos", "POST": "CreatePhoto", "DELETE": "DeletePhoto"}


def verify_token(token, userpool_id, app_client_id):

    keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
        region, userpool_id
    )

    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode("utf-8"))["keys"]

    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]["kid"]:
            key_index = i
            break
    if key_index == -1:
        print("Public key not found in jwks.json")
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit(".", 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print("Signature verification failed")
        return False
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims["exp"]:
        print("Token is expired")
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims["aud"] != app_client_id:
        print("Token was not issued for this audience")
        return False
    # now we can use the claims
    return claims


def _get_entities(token_claims: Dict) -> List:
    data_entities: List[Dict] = []
    # add groups from token
    if groups := token_claims.get("cognito:groups"):
        for group in groups:
            data_entities.append(
                {
                    "identifier": asdict(
                        Identifier(
                            entityType="MyPolicyStore::UserGroup", entityId=group
                        )
                    )
                }
            )

    # add user and group parents
    user_entity = {
        "identifier": asdict(
            Identifier(
                entityType="MyPolicyStore::User",
                entityId=token_claims["cognito:username"],
            )
        ),
        "parents": [],
    }

    if groups := token_claims.get("cognito:groups"):
        for role in groups:
            user_entity["parents"].append(
                asdict(Identifier(entityType="MyPolicyStore::UserGroup", entityId=role))
            )
    data_entities.append(user_entity)
    return data_entities


def check_authorization(
    principal: str,
    action: str,
    resource: str,
    claims: Dict[str, Any],
) -> str:
    authz_response = avp_client.is_authorized(
        policyStoreId=POLICY_STORE_ID,
        principal=asdict(
            Identifier(entityType="MyPolicyStore::User", entityId=principal)
        ),
        resource=asdict(
            Identifier(entityType="MyPolicyStore::Photo", entityId=resource)
        ),
        action={"actionType": "MyPolicyStore::Action", "actionId": action},
        entities={"entityList": _get_entities(claims)},
    )
    print(authz_response)
    return authz_response


# GENERATE IAM POLICY RESPONSE FOR API AUTHORIZER RESPONSE
def generate_response(principal_id: str, effect: str, resource: str) -> Dict:
    policy = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        },
    }

    return policy


def handler(event, context):
    token = event["headers"]["Auth-Token"]
    httpMethod = event["httpMethod"]
    params = event["queryStringParameters"]
    userpool_id = params["userpool_id"]
    app_client_id = params["client_id"]
    resource = params["resource"]

    verified_token = verify_token(token, userpool_id, app_client_id)

    if verified_token:
        result = check_authorization(
            verified_token["cognito:username"],
            action[httpMethod],
            resource,
            verified_token,
        )
        policy_response = generate_response(
            principal_id=verified_token["cognito:username"],
            effect=result["decision"],
            resource=event["methodArn"],
        )
        return policy_response
    raise Exception("Unauthorized")


# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
# if __name__ == "__main__":
#     # for testing locally you can enter the JWT ID Token here
#     event = {
#         "httpMethod": "DELETE",
#         "queryStringParameters": {
#             "token": "eyJraWQiOiJSdm1hblpHaXA0NHRVa3o1MEZcL1RUMDBoZGtuaHFMOWxXMnc5cEV6emYrQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI0NDM4YzQwOC1kMDUxLTcwOGYtODY0Ni0yMDg0MGU3Yjk4MTEiLCJjb2duaXRvOmdyb3VwcyI6WyJjcmVhdG9yIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfYUdHRjVvZzA3IiwiY29nbml0bzp1c2VybmFtZSI6InRlc3RfdXNlciIsIm9yaWdpbl9qdGkiOiI5ZTYyNDAxOS1lZWQzLTRiMjctOTg3Ny02ZDcwYWU0Yzk0MTciLCJhdWQiOiI2czdxNDU1dDBrbmp0aGtxdG85MXE3ZG5yMSIsImV2ZW50X2lkIjoiYWRhNDBlNmEtNWQ2MC00M2JmLWIxYTctMzEzNzM4MThiZmI4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MTg0ODI1MjcsImV4cCI6MTcxODQ4NjEyNywiaWF0IjoxNzE4NDgyNTI3LCJqdGkiOiJhYzJkNDI0Mi1jZjg5LTQxZjMtOWQ4My01OTU5ZGE0MTEzYmYiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.GwwHFcST9MrLM-w1MSl4FjP_odSlYOGXC5F6USjPcyYdRdoKQ1h5I0nt1LrgHFMtT8GHUxLEAvyHMf4PXXlr38s2_nG24yzSm0yP97WpMDUlSKpFkdIuXryFEL1F6MFCev5kznOxGNXZKYRJ6dA52soDRLHz-zFEerrI3kOKlaCZwGK74Sas7I3x9LD_2m_rfml2zNGeiM8T1gOKP53X7w7XzDFOnzQIBxQLxi_5hFxh8ulfIQMAKcY7Bupjq-jNfsqdTkpc4EDZart71ypO6dBdxaf_GgorWiqX1q0I-1GA0wualQBlQ24KiLxdj5dZX3WDRMpMG7adCuPYgErqWA",
#             "resource": "sunset.jpg",
#             "userpool_id": "us-east-1_aGGF5og07",
#             "client_id": "6s7q455t0knjthkqto91q7dnr1",
#             "policy_store_id": "GvRbNuam2fdkeNQXeSq17C",
#         },
#     }
#     handler(event, None)
