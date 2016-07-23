from .base_case import BaseCase
from api.tests import factories
from rest_framework import status
import json
from api.models import PickemsUser

class UsersTest(BaseCase):
    __test__ = True
    url = '/api/users'
    attributes = ['username', 'first_name', 'last_name', 'email']
    relationships = ['teams']
    post_data = {
        'data': {
            'type': 'users',
            'attributes': {
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'testing',
            }
        }
    }
    put_data = {
        'data': {
            'type': 'users',
            'attributes': {
                'username': 'newuser2',
                'first_name': 'New2',
                'last_name': 'User2',
                'email': 'newuser2@example.com',
                'password': 'testing2'
            }
        }
    }

    def setUp(self):
        super(UsersTest, self).setUp()

        # create 4 users
        for i in range(0, 4):
            factories.PickemsUserFactory()

    def test_post_endpoint(self):
        response = self.client.post(self.url, json.dumps(self.post_data), content_type='application/vnd.api+json')
        assert response.status_code == status.HTTP_201_CREATED
        data = json.loads(response.content).get('data')
        assert data.get('type') == self.post_data['data']['type']

        # make sure the user was created
        assert PickemsUser.objects.get(id=data['id'])

    def test_patch_endpoint(self):
         # make sure user is still there
        user = PickemsUser.objects.first()
        assert user

        response = self.client.patch('{}/{}'.format(self.url, user.id), json.dumps(self.put_data), content_type='application/vnd.api+json')
        assert response.status_code == status.HTTP_200_OK

        updatedUser = PickemsUser.objects.get(id=user.id)
        for attr in self.attributes:
            assert getattr(updatedUser, attr, 'not-equal') == self.put_data['data']['attributes'][attr]

    def test_delete_endpoint(self):
        # make sure user is still there
        user = PickemsUser.objects.first()
        assert user

        # make the request
        response = self.client.delete('{}/{}'.format(self.url, user.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert len(PickemsUser.objects.filter(id=user.id)) == 0
