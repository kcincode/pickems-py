from .base_case import BaseCase
from api.tests import factories
import json


class UsersTest(BaseCase):
    __test__ = True
    url = '/api/users'
    attributes = ['username', 'first_name', 'last_name', 'email', 'is_staff']
    post_data = {
        'data': {
            'attributes': {
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'testing'
            }
        }
    }

    def setUp(self):
        super(UsersTest, self).setUp()

        # create 4 users
        for i in range(0, 4):
            factories.PickemsUserFactory()

    def test_post_endpoint(self):
        response = self.client.post(self.url, self.post_data)
        assert response.status_code == 201
        data = json.loads(response.content).get('data')

        print(data)
        print(self.post_data)

