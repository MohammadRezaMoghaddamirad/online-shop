"""
تست‌های ثبت‌نام
"""
import pytest


@pytest.mark.django_db
class TestRegister:
    """تست ثبت‌نام کاربر جدید"""

    url = '/api/v1/auth/register/'

    def test_register_success(self, api_client):
        """ثبت‌نام موفق"""
        response = api_client.post(self.url, {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'NewUser@1234',
            'password2': 'NewUser@1234',
            'phone': '09121111111',
            'address': 'Tehran'
        })

        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert response.data['user']['role'] == 'customer'

    def test_register_password_mismatch(self, api_client):
        """رمز و تکرارش یکسان نیستند"""
        response = api_client.post(self.url, {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'NewUser@1234',
            'password2': 'Different@1234'
        })

        assert response.status_code == 400
        assert 'password' in response.data['error']['details']

    def test_register_duplicate_username(self, api_client, customer_user):
        """username تکراری"""
        response = api_client.post(self.url, {
            'username': 'test_customer',
            'email': 'new@test.com',
            'password': 'NewUser@1234',
            'password2': 'NewUser@1234'
        })

        assert response.status_code == 400
        assert 'username' in response.data['error']['details']