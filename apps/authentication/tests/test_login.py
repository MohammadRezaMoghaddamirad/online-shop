"""
تست‌های ورود
"""
import pytest


@pytest.mark.django_db
class TestLogin:
    """تست ورود کاربر"""

    url = '/api/v1/auth/login/'

    def test_login_success(self, api_client, customer_user):
        """ورود موفق"""
        response = api_client.post(self.url, {
            'username': 'test_customer',
            'password': 'Customer@1234'
        })

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, api_client, customer_user):
        """رمز عبور اشتباه"""
        response = api_client.post(self.url, {
            'username': 'test_customer',
            'password': 'WrongPassword'
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        """کاربر وجود ندارد"""
        response = api_client.post(self.url, {
            'username': 'ghost',
            'password': 'whatever'
        })

        assert response.status_code == 401