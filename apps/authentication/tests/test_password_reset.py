"""
تست‌های فراموشی و بازیابی رمز عبور
"""
import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

NEW_PASSWORD = 'BrandNew@98765'


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    """شمارندهٔ throttle بین تست‌ها پاک شود"""
    cache.clear()
    yield
    cache.clear()


def uid_and_token(user):
    return (
        urlsafe_base64_encode(force_bytes(user.pk)),
        default_token_generator.make_token(user),
    )


@pytest.mark.django_db
class TestForgotPassword:
    url = '/api/v1/auth/password/forgot/'

    def test_existing_email_sends_mail(self, api_client, customer_user, mailoutbox):
        response = api_client.post(self.url, {'email': customer_user.email})

        assert response.status_code == 200
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [customer_user.email]
        assert 'uid=' in mailoutbox[0].body
        assert 'token=' in mailoutbox[0].body

    def test_unknown_email_gives_same_response_and_no_mail(self, api_client, customer_user, mailoutbox):
        known = api_client.post(self.url, {'email': customer_user.email})
        unknown = api_client.post(self.url, {'email': 'nobody@test.com'})

        assert unknown.status_code == 200
        assert unknown.data == known.data
        assert len(mailoutbox) == 1  # فقط برای ایمیل موجود

    def test_inactive_user_gets_no_mail(self, api_client, customer_user, mailoutbox):
        customer_user.is_active = False
        customer_user.save()

        response = api_client.post(self.url, {'email': customer_user.email})

        assert response.status_code == 200
        assert len(mailoutbox) == 0

    def test_invalid_email_rejected(self, api_client):
        response = api_client.post(self.url, {'email': 'not-an-email'})

        assert response.status_code == 400
        assert 'email' in response.data['error']['details']

    def test_throttled_after_limit(self, api_client):
        for _ in range(5):
            assert api_client.post(self.url, {'email': 'a@test.com'}).status_code == 200

        assert api_client.post(self.url, {'email': 'a@test.com'}).status_code == 429


@pytest.mark.django_db
class TestResetPassword:
    url = '/api/v1/auth/password/reset/'

    def payload(self, user, **overrides):
        uid, token = uid_and_token(user)
        data = {
            'uid': uid,
            'token': token,
            'password': NEW_PASSWORD,
            'confirm_password': NEW_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_reset_success(self, api_client, customer_user):
        response = api_client.post(self.url, self.payload(customer_user))

        assert response.status_code == 200
        customer_user.refresh_from_db()
        assert customer_user.check_password(NEW_PASSWORD)

    def test_token_cannot_be_reused(self, api_client, customer_user):
        data = self.payload(customer_user)
        assert api_client.post(self.url, data).status_code == 200

        again = api_client.post(self.url, data)

        assert again.status_code == 400
        assert 'token' in again.data['error']['details']

    def test_invalid_token_rejected(self, api_client, customer_user):
        response = api_client.post(self.url, self.payload(customer_user, token='bad-token'))

        assert response.status_code == 400
        assert 'token' in response.data['error']['details']
        customer_user.refresh_from_db()
        assert customer_user.check_password('Customer@1234')

    def test_invalid_uid_rejected(self, api_client, customer_user):
        response = api_client.post(self.url, self.payload(customer_user, uid='!!!'))

        assert response.status_code == 400
        assert 'token' in response.data['error']['details']

    def test_password_mismatch_rejected(self, api_client, customer_user):
        response = api_client.post(
            self.url, self.payload(customer_user, confirm_password='Different@123')
        )

        assert response.status_code == 400
        assert 'confirm_password' in response.data['error']['details']

    def test_weak_password_rejected(self, api_client, customer_user):
        response = api_client.post(
            self.url,
            self.payload(customer_user, password='12345678', confirm_password='12345678'),
        )

        assert response.status_code == 400
        assert 'password' in response.data['error']['details']

    def test_old_refresh_tokens_are_blacklisted(self, api_client, customer_user):
        RefreshToken.for_user(customer_user)  # یک نشست قدیمی

        response = api_client.post(self.url, self.payload(customer_user))

        assert response.status_code == 200
        assert BlacklistedToken.objects.filter(token__user=customer_user).count() == 1
