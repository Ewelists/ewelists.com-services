import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import update

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_update_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}",
        "path": "/lists/cf19fb62",
        "httpMethod": "PUT",
        "body": "{\n    \"attribute_name\": \"title\",\n    \"attribute_value\": \"My new title\"\n}",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "GB",
            "Content-Type": "text/plain",
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "d38bfa3c-26b3-4a42-acfa-ecc30a12d767",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 f76142b838785e2eec49408a3d9d8285.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "pUhW1u14GSPTlHCQed4C5eTsM3Biv_ca3cDVCh9hbcnZ3_e4z0CgVw==",
            "x-amz-content-sha256": "51f3f8790f9b06462165164ab5e1bf33fd64f8230e962c445681a63555e04429",
            "x-amz-date": "20191007T160043Z",
            "X-Amzn-Trace-Id": "Root=1-5d9b612b-c2a6fbd0452771f0b0155f70",
            "X-Forwarded-For": "5.81.150.55, 70.132.15.71",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": "null",
        "multiValueQueryStringParameters": "null",
        "pathParameters": {
            "id": "cf19fb62"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "4j13uq",
            "resourcePath": "/lists/{id}",
            "httpMethod": "PUT",
            "extendedRequestId": "BMwexGf4DoEFoJA=",
            "requestTime": "07/Oct/2019:16:00:43 +0000",
            "path": "/test/lists/cf19fb62",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570464043231,
            "requestId": "c410dfa4-713a-4ac3-afe5-2e3ab3d4066f",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": "ABCDEFGPDMJL4EB35H6H",
                "cognitoAuthenticationType": "authenticated",
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:42cf26f5-407c-47cf-bcb6-f70cd63ac119",
                "userArn": "arn:aws:sts::123456789012:assumed-role/Ewelists-test-CognitoAuthRole/CognitoIdentityCredentials",
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials"
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "isBase64Encoded": "false"
    }


@pytest.fixture
def dynamodb_mock():
    table_name = 'lists-unittest'

    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'listId',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'listId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    item = {
        'userId': 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c',
        'userPoolSub': '42cf26f5-407c-47cf-bcb6-f70cd63ac119',
        'listId': '1234abcd',
        'title': 'My Test List',
        'description': 'Test description for the list.',
        'occasion': 'Birthday',
        'createdAt': 1570552083
    }

    table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


# Add tests
