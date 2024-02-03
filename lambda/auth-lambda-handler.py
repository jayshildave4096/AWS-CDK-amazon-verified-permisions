import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

region = 'us-east-1'


def verify_token(token, userpool_id, app_client_id):

    keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode('utf-8'))['keys']
    
    token = event['token']
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
    print(claims)
    return claims


def lambda_handler(event, context):
    token = event['token'] 
    userpool_id = event['userpool_id']
    app_client_id = event['client_id']

    verify_token(token,userpool_id, app_client_id)

    #AVP verification 


# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': 'eyJraWQiOiJwUzEwVjVHdXdIaHdRR2ZQOXRPNzFEYktjZTBQREhnMkNuM1wvaXZlbVFPMD0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NDU4NDQ5OC1kMDExLTcwZDEtZGRmNi1lZDM3YjRkYjczMjAiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX0pLU1YyWlNDWCIsImNvZ25pdG86dXNlcm5hbWUiOiJqYXlzaGlsMyIsIm9yaWdpbl9qdGkiOiIxMzQ4NTZiZC04NTlkLTQ4NGMtOGNhMS0zMTZiNDk4NmFjZGMiLCJhdWQiOiI1NWFrMmRsZ2hza2RmNWdqdm5tOWlsbnNyMiIsImV2ZW50X2lkIjoiY2EzOTZjOWQtMGMxNy00ZmY4LTkxYzctZWZlYjM0ZTlhNmFiIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MDY5MTk0NjYsImV4cCI6MTcwNjkyMzA2NiwiaWF0IjoxNzA2OTE5NDY2LCJqdGkiOiJjYzk3ODVkYi02MzUzLTRkZDMtOWQwMS1hMGRhZTYzYmNlOGQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.ij3d8PgStIVscXvzG_RISMCJi1Ak2IJhJbtLWx12Q4dPjG2eLMQL-IxxTS3eHmhE6cddYjjq1awWyle7zAQYhtsAv96NjXL4UF_ukQKgikyNW26KIf5Amlsxu95Gs_qBAxGcryytuthhIROqaFEKUwOtry20ghcJapzsU5RBc8KIEmUUlqKzRsrhll6Y7o1sMLmynHDm59NOCtFXCPpDOEAdhgcjxj63HuVj-U991r3uPt1z-d3LtpmutT7XqG1p7-yfz7lauls0Y3LwfsJ9YdheYmoDRwkdM79f0CHI-cX8mcYUPNBcKXSR_Ue5-3dw5IdR_lkd-LuOpp6zEnBVOA',
             'userpool_id':'us-east-1_JKSV2ZSCX',
             'client_id':'55ak2dlghskdf5gjvnm9ilnsr2'}
    lambda_handler(event, None)