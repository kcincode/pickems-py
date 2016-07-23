import pytest
from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnDict
from api.tests import factories
from rest_framework_jwt.settings import api_settings
from rest_framework.utils.serializer_helpers import ReturnList
import json

pytestmark = pytest.mark.django_db(transaction=True)


class BaseCase(APITestCase):
    __test__ = False
    url = ''
    attributes = []
    relationships = []
    get_number = 5

    def setUp(self):
        # create the user for authentication
        user = factories.PickemsUserFactory(
            username='authuser',
            email='authuser@example.com',
            password='testing'
        )

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT ' + token,
            HTTP_ACCEPT='application/vnd.api+json',
        )


    def test_get_endpoints(self):
        # make the request
        response = self.client.get(self.url)

        # test the results
        assert response.status_code == 200
        data = json.loads(response.content).get('data')
        assert isinstance(data, list)
        assert len(data) == self.get_number

        # loop through results and check each single request
        for item in data:
            single_response = self.client.get('{}/{}'.format(self.url, item.get('id')))
            assert single_response.status_code == 200
            assert isinstance(single_response.data, ReturnDict)
            single_data = json.loads(single_response.content).get('data')
            print(single_data)

            for attribute in self.attributes:
                print(attribute)
                assert attribute in single_data['attributes'].keys()

            for relationship in self.relationships:
                print(relationship)
                assert relationship in single_data['relationships'].keys()

    def test_post_endpoint(self):
        # make the request
        response = self.client.post('{}/{}'.format(self.url, 1))
        assert response.status_code == 405

    def test_invalid_post_endpoint(self):
        response = self.client.post(self.url, json.dumps({}), content_type='application/vnd.api+json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_endpoint(self):
        # make the request
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('{}/{}'.format(self.url, 1))

        assert response.status_code == 405

    def test_invalid_patch_endpoint(self):
        response = self.client.patch('{}/{}'.format(self.url, 1), json.dumps({}), content_type='application/vnd.api+json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_delete_endpoint(self):
    #     # make the request
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.delete('{}/{}'.format(self.url, 1))

    #     assert response.status_code == 405
