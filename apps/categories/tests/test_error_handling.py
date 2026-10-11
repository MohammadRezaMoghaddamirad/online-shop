"""
تست مدیریت یکسان خطاهای API
"""
import pytest


@pytest.mark.django_db
class TestErrorHandling:
    """همه خطاها با قالب {"success": false, "error": {...}} برمی‌گردند"""

    def test_delete_category_with_products_returns_409(self, admin_client, product):
        """قبلاً ProtectedError خطای ۵۰۰ می‌داد"""
        response = admin_client.delete(f'/api/v1/categories/{product.category.id}/')

        assert response.status_code == 409
        assert response.data['success'] is False
        assert response.data['error']['code'] == 'protected'

    def test_delete_empty_category_succeeds(self, admin_client, category):
        response = admin_client.delete(f'/api/v1/categories/{category.id}/')

        assert response.status_code == 204

    def test_validation_error_format(self, admin_client):
        response = admin_client.post('/api/v1/categories/', {'name': 'a'})

        assert response.status_code == 400
        assert response.data['success'] is False
        assert response.data['error']['code'] == 'validation_error'
        assert 'name' in response.data['error']['details']

    def test_unauthenticated_error_format(self, api_client):
        response = api_client.get('/api/v1/carts/')

        assert response.status_code == 401
        assert response.data['success'] is False

    def test_permission_denied_error_format(self, customer_client):
        response = customer_client.get('/api/v1/orders/admin/')

        assert response.status_code == 403
        assert response.data['success'] is False

    def test_checkout_empty_cart_error_format(self, customer_client):
        response = customer_client.post('/api/v1/orders/checkout/', {})

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'سبد خرید' in response.data['error']['message']
