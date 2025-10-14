Here's the Python test code for the User model login functionality using PyTest and a mock Redux store:

```python
from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def mock_user():
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def api_client():
    return APIClient()

@patch('django.contrib.auth.get_user_model')
def test_login(mock_get_user_model, mock_user):
    mock_get_user_model.return_value = User
    url = reverse('rest-auth:login')
    data = {'username': 'testuser', 'password': 'testpassword'}

    with mock_user:
        client = api_client()
        response = client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == mock_user.email
        mock_get_user_model.assert_called_once_with()
```

This test suite uses PyTest fixtures to create a mock user and an API client, then tests the login functionality by making a POST request to the login endpoint with the provided data. The response is checked for status code, username, and email to ensure successful authentication. Additionally, it verifies that `django.contrib.auth.get_user_model` was called once to ensure that the correct user model is being used.