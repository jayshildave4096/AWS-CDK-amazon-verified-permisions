import boto3
import json
import time
from typing import Dict
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from dataclasses import asdict, dataclass

region = 'us-east-1'
avp_client = boto3.client('verifiedpermissions')

@dataclass
class Identifier:
    entityId: str
    entityType: str

POLICY_STORE_ID = 'Y7xjX1HMZUsfMDB3wyEJxb'


def verify_token(token, userpool_id, app_client_id):

    keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode('utf-8'))['keys']
    
    # token = event['token']
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    return claims

def check_authorization(policy_store_id: str, principal_id: str, action: str, resource: str, claims: Dict, user_attributes: Dict) -> str:
    principal = Identifier(entityType='MyPolicyStore::User', entityId=principal_id)
    action = {'actionType': 'Action', 'actionId': action}
    resource = Identifier(entityType='MyPolicyStore::Photo', entityId=resource)

    print(
        f'store id:{policy_store_id}, principal:{asdict(principal)}, action:{action}, resource:{asdict(resource)}'
    )
    authz_response = avp_client.is_authorized(
        policyStoreId=policy_store_id,
        principal=asdict(principal),
        resource=asdict(resource),
        action=action
    )
    print(authz_response)
    return authz_response


def handler(event, context):
    params = event['queryStringParameters']
    token = params['token'] 
    userpool_id = params['userpool_id']
    app_client_id = params['client_id']
    policy_store_id = params['policy_store_id']
    httpMethod = event['httpMethod']
    resource = event['resource'][event['resource'].index('/'):]


    token = verify_token(token,userpool_id, app_client_id)
    result = check_authorization(policy_store_id, 'jayshil', 'CreatePhoto', 'test.jpg', token, {})

    if result['decision'] == 'ALLOW':
        return {
        'statusCode': 200,
        'body': json.dumps({
            'msg': f"Congrats! You've successfully verified",
        })
    }
    else:
        return {
        'statusCode': 401,
        'body': json.dumps({
            'msg': f"Failed to verify"
        })
    }


    #AVP verification 

# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
# if __name__ == '__main__':
#     # for testing locally you can enter the JWT ID Token here
#     event = {'token': 'eyJraWQiOiJKRjVPVTJIcXE4dVwvV2Z3Z09pS3g3cHJcL1F3aTB6VGN0dytYczZCXC9kaHEwPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI1NDMyN2M2ZC01MWYzLTQ4OWMtOTE1YS0zZGY3OGJjMmU5YjAiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX0RVaThuZXNxZyIsImNvZ25pdG86dXNlcm5hbWUiOiJqYXlzaGlsMyIsIm9yaWdpbl9qdGkiOiI3MDJmNzBmMi02YTczLTQyYzUtOGE1NS1iNTAyMjEzMDE1MzAiLCJhdWQiOiI2NjQwc2o0cGFzamE2cXNyMHFnbTQ2M245ayIsImV2ZW50X2lkIjoiNDM2MjZiMWEtYzNhMS00YTAwLWI3NjUtYmFjNzUzYjg4MTI5IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MTU5NTYwNjcsImV4cCI6MTcxNTk1OTY2NywiaWF0IjoxNzE1OTU2MDY3LCJqdGkiOiJkNDMxYzJjYS1iYjM5LTRhMmEtOTVlYy03MTA1MjQ2MWNjYjUiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.cZVMISwN5jf2HiTuXd1LAxOjtQE5Zdmjc1iASE7B8sxut48RFWTf1sg4WzM8lbP_DoM2HDU65AHtWr0li6jTH7Lut8E7RYpJ5URc1XotkD34wVuhisgIPIunMaA2bsvX-TWUj0WB1g6JbfNnJRsLR1jqmT7YbQJ_Ruwe0EqisQksvvhg-9DxapjSTRmoYk8NIAPAGYmSYZDmEpkF4_h2pNPoNdzReUl26xIXBys7yRex1Zx9WDPvyKi-2IhCvS0RzVdFdNK84bSxIaGe3LK1rsSvVv2I0uTwXWC2dzlWEQYcgNlZzTHe8scaChvWnQuTodvrcJRcptkFrO4B-4cu5A',
#              'userpool_id':'us-east-1_DUi8nesqg',
#              'client_id':'6640sj4pasja6qsr0qgm463n9k',
#              'policy_store_id':'Y7xjX1HMZUsfMDB3wyEJxb'}
#     lambda_handler(event, None)