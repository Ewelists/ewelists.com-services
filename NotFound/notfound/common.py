# A collection of methods that are common across all modules.
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response


def get_table_name(osenv):
    try:
        table_name = osenv['TABLE_NAME']
        logger.info("TABLE_NAME environment variable value: " + table_name)
    except KeyError:
        logger.error('TABLE_NAME environment variable not set correctly.')
        raise Exception('TABLE_NAME environment variable not set correctly.')

    return table_name


def get_identity(event, osenv):
    identity = {}

    try:
        userArn = event['requestContext']['identity']['userArn']
        cognito_user_id = event['requestContext']['identity']['cognitoIdentityId']
        cognito_authentication_provider = event['requestContext']['identity']['cognitoAuthenticationProvider']
    except KeyError:
        logger.error("There was no identity context in API event.")
        raise Exception("There was no identity context in API event.")

    # Check to see if request was generated by postman, which doesn't authenticate via cognito.
    pattern = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser")
    if pattern.match(userArn):
        logger.info('Request was from postman, using API test identity.')
        os_identity = get_postman_identity(osenv)
        identity["cognitoIdentityId"] = os_identity["POSTMAN_IDENTITY_ID"]
        identity["userPoolSub"] = os_identity["POSTMAN_USERPOOL_SUB"]
    else:
        if cognito_user_id is None:
            raise Exception("There was no cognitoIdentityId in the API event.")

        identity["cognitoIdentityId"] = cognito_user_id
        identity["userPoolSub"] = cognito_authentication_provider.split(':')[-1]

        logger.info('cognitoIdentityId was retrieved from event.')

    return identity


def get_postman_identity(osenv):
    os_identity = {}
    try:
        os_identity["POSTMAN_IDENTITY_ID"] = osenv['POSTMAN_IDENTITY_ID']
        os_identity["POSTMAN_USERPOOL_SUB"] = osenv['POSTMAN_USERPOOL_SUB']
    except KeyError:
        logger.error('POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.')
        raise Exception('POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.')

    return os_identity


def get_product_id(event):
    try:
        product_id = event['pathParameters']['id']
        logger.info("Product ID: " + product_id)
    except Exception:
        logger.error("API Event did not contain a Product ID in the path parameters.")
        raise Exception('API Event did not contain a Product ID in the path parameters.')

    return product_id
