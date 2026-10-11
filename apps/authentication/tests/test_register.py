"""
تست‌های ثبت‌نام
"""
import pytest


@pytest.mark.django_db
class TestRegister:
    """تست ثبت‌نام کاربر جدید (فقط با ایمیل)"""

    url = '/api/v1/auth/register/'

    def test_register_success(self, api_client):
        """ثبت‌نام موفق"""
        response = api_client.post(self.url, {
            'email': 'new@test.com',
            'password': 'NewUser@1234',
            'confirm_password': 'NewUser@1234',
            'phone': '09121111111',
        })

        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'new@test.com'
        assert response.data['user']['username'] == 'new@test.com'
        assert response.data['user']['role'] == 'customer'

    def test_register_password_mismatch(self, api_client):
        """رمز و تکرارش یکسان نیستند"""
        response = api_client.post(self.url, {
            'email': 'new@test.com',
            'password': 'NewUser@1234',
            'confirm_password': 'Different@1234',
        })

        assert response.status_code == 400
        assert 'confirm_password' in response.data['error']['details']

    def test_register_duplicate_email(self, api_client, customer_user):
        """ایمیل تکراری"""
        response = api_client.post(self.url, {
            'email': customer_user.email,
            'password': 'NewUser@1234',
            'confirm_password': 'NewUser@1234',
        })

        assert response.status_code == 400
        assert 'email' in response.data['error']['details']