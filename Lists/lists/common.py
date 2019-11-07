# A collection of methods that are common across all modules.
import logging
import re
import json
from lists.entities import List, Product

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def get_table_name(osenv):
    try:
        table_name = osenv['TABLE_NAME']
        logger.info("TABLE_NAME environment variable value: " + table_name)
    except KeyError:
        logger.error('TABLE_NAME environment variable not set correctly.')
        raise Exception('TABLE_NAME environment variable not set correctly.')

    return table_name


def get_table_index(osenv):
    try:
        index_name = osenv['INDEX_NAME']
        logger.info("INDEX_NAME environment variable value: " + index_name)
    except KeyError:
        logger.error('INDEX_NAME environment variable not set correctly.')
        raise Exception('INDEX_NAME environment variable not set correctly.')

    return index_name


def get_userpool_id(osenv):
    try:
        userpool_id = osenv['USERPOOL_ID']
        logger.info("USERPOOL_ID environment variable value: " + userpool_id)
    except KeyError:
        logger.error('USERPOOL_ID environment variable not set correctly.')
        raise Exception('USERPOOL_ID environment variable not set correctly.')

    return userpool_id


def confirm_owner(cognito_user_id, list_id, response_items):
    list_owner_id = None
    for item in response_items:
        if item['SK']['S'].startswith("USER"):
            logger.info("List Owner Item: {}".format(item))
            logger.info("List Owner: {}".format(item['listOwner']['S']))
            list_owner_id = item['listOwner']['S']

    if list_owner_id != cognito_user_id:
        logger.info("Owner of List ID {} did not match user id of requestor: {}.".format(list_id, cognito_user_id))
        raise Exception("Owner of List ID {} did not match user id of requestor: {}.".format(list_id, cognito_user_id))

    return True


def confirm_list_shared_with_user(cognito_user_id, list_id, response_items):
    shared_user = 'SHARE#' + cognito_user_id
    for item in response_items:
        if item['SK']['S'] == shared_user:
            logger.info("Confirmed list {} is shared with user {}".format(list_id, cognito_user_id))
            return True

    logger.info("List ID {} did not have a shared item with user {}.".format(list_id, cognito_user_id))
    raise Exception("List ID {} did not have a shared item with user {}.".format(list_id, cognito_user_id))


def generate_list_object(response_items):
    list = {"list": None, "products": []}

    for item in response_items:
        if item['SK']['S'].startswith("USER"):
            logger.info("List Owner Item: {}".format(item))
            list['list'] = List(item).get_details()
        elif item['SK']['S'].startswith("PRODUCT"):
            logger.info("Product Item: {}".format(item))
            product = Product(item).get_details()
            list['products'].append(product)

    return list


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


def get_list_id(event):
    try:
        list_id = event['pathParameters']['id']
        logger.info("List ID: " + list_id)
    except Exception:
        logger.error("API Event did not contain a List ID in the path parameters.")
        raise Exception('API Event did not contain a List ID in the path parameters.')

    return list_id


def get_product_id(event):
    try:
        product_id = event['pathParameters']['productid']
        logger.info("Product ID: " + product_id)
    except Exception:
        logger.error("API Event did not contain a Product ID in the path parameters.")
        raise Exception('API Event did not contain a Product ID in the path parameters.')

    return product_id


def get_quantity(event):
    try:
        body_object = json.loads(event['body'])
        quantity = body_object['quantity']
        logger.info("Quantity: " + str(quantity))
    except Exception:
        logger.error("API Event did not contain the quantity in the body.")
        raise Exception('API Event did not contain the quantity in the body.')

    return quantity


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
