import json

def handler(event, context):

    func_arn = context.invoked_function_arn
    func_alias = func_arn.rsplit(':', 1)[-1]

    return {
        'statusCode': 200,
        'body': json.dumps({
            'msg': f"Congrats! You've successfully hit the  API endpoint"
        })
    }
