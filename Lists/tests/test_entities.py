import pytest
from lists.entities import User, List, Product
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def response_items():
    response_items = [
        {'PK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'email': {'S': 'test.user@gmail.com'}, 'name': {'S': 'Test User'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Api Child's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'description': {'S': 'A gift list for Api Childs birthday.'}, 'eventDate': {'S': '2019-09-01'}},
        {"quantity": {"N": "1"}, "reserved": {"N": "0"}, "SK": {"S": "PRODUCT#1009"}, "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}}
    ]

    return response_items


class TestUser:
    def test_get_basic_details(self, response_items):
        user = User(response_items[0]).get_basic_details()

        # assert user['name'] == 'Test User', "User name was not Test User."
        assert user['email'] == 'test.user@gmail.com', "User email was not test.user@gmail.com."


class TestList:
    def test_get_details(self, response_items):
        list = List(response_items[1]).get_details()

        assert list['listId'] == '12345678-list-0001-1234-abcdefghijkl', "List ID was not 12345678-list-0001-1234-abcdefghijkl."
        assert list['title'] == "Api Child's 1st Birthday", "List Title was not as expected."
        assert list['description'] == "A gift list for Api Childs birthday.", "List description was not as expected."
        assert list['occasion'] == 'Birthday', "List occasion was not Birthday."


class TestProduct:
    def test_get_details(self, response_items):
        product = Product(response_items[2]).get_details()

        assert product['productId'] == '1009', "Product ID was not 1009."
        assert product['quantity'] == 1, "Product quanity was not 1."
        assert product['reserved'] == 0, "Product reserved quantity was not 0."
