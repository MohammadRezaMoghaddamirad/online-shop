"""
تست‌های سبد خرید
"""
import pytest

ADD_URL = '/api/v1/carts/add/'
CART_URL = '/api/v1/carts/'


def _add(client, product, quantity):
    return client.post(ADD_URL, {'product_id': product.id, 'quantity': quantity})


@pytest.mark.django_db
class TestAddToCart:
    """افزودن محصول به سبد"""

    def test_add_success_and_total_price(self, customer_client, product):
        response = _add(customer_client, product, 2)

        assert response.status_code == 200
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['quantity'] == 2
        assert int(response.data['total_price']) == 100_000_000

    def test_add_same_product_increases_quantity(self, customer_client, product):
        _add(customer_client, product, 2)
        response = _add(customer_client, product, 3)

        assert response.status_code == 200
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['quantity'] == 5

    def test_add_more_than_stock_leaves_cart_empty(self, customer_client, product):
        """باگ قبلی: آیتم با تعداد ۱ در سبد می‌ماند"""
        response = _add(customer_client, product, product.stock + 1)

        assert response.status_code == 400
        assert customer_client.get(CART_URL).data['items'] == []

    def test_add_more_than_stock_keeps_existing_quantity(self, customer_client, product):
        _add(customer_client, product, 8)
        response = _add(customer_client, product, 3)  # 8 + 3 > 10

        assert response.status_code == 400
        items = customer_client.get(CART_URL).data['items']
        assert len(items) == 1
        assert items[0]['quantity'] == 8

    def test_out_of_stock_product_cannot_be_added(self, customer_client, product):
        product.stock = 0
        product.save()

        response = _add(customer_client, product, 1)

        assert response.status_code == 400
        assert customer_client.get(CART_URL).data['items'] == []

    def test_inactive_product_not_found(self, customer_client, product):
        product.is_active = False
        product.save()

        assert _add(customer_client, product, 1).status_code == 404

    def test_product_of_inactive_category_not_found(self, customer_client, product):
        product.category.is_active = False
        product.category.save()

        assert _add(customer_client, product, 1).status_code == 404

    def test_anonymous_user_cannot_use_cart(self, api_client, product):
        assert api_client.get(CART_URL).status_code == 401
        assert _add(api_client, product, 1).status_code == 401


@pytest.mark.django_db
class TestCartItems:
    """تغییر و حذف آیتم‌ها"""

    def test_update_quantity(self, customer_client, product):
        item_id = _add(customer_client, product, 1).data['items'][0]['id']

        response = customer_client.patch(
            f'{CART_URL}items/{item_id}/', {'quantity': 4}
        )

        assert response.status_code == 200
        assert response.data['items'][0]['quantity'] == 4

    def test_update_quantity_over_stock(self, customer_client, product):
        item_id = _add(customer_client, product, 1).data['items'][0]['id']

        response = customer_client.patch(
            f'{CART_URL}items/{item_id}/', {'quantity': product.stock + 1}
        )

        assert response.status_code == 400

    def test_remove_item(self, customer_client, product):
        item_id = _add(customer_client, product, 1).data['items'][0]['id']

        response = customer_client.delete(f'{CART_URL}items/{item_id}/remove/')

        assert response.status_code == 200
        assert response.data['items'] == []

    def test_remove_missing_item_returns_404(self, customer_client):
        response = customer_client.delete(f'{CART_URL}items/999999/remove/')

        assert response.status_code == 404

    def test_clear_cart(self, customer_client, product):
        _add(customer_client, product, 2)

        assert customer_client.delete(f'{CART_URL}clear/').status_code == 204
        assert customer_client.get(CART_URL).data['items'] == []

    def test_user_cannot_touch_other_users_item(self, customer_client, admin_client, product):
        """هر کاربر فقط به سبد خودش دسترسی دارد"""
        item_id = _add(customer_client, product, 1).data['items'][0]['id']

        response = admin_client.delete(f'{CART_URL}items/{item_id}/remove/')

        assert response.status_code == 404
        assert len(customer_client.get(CART_URL).data['items']) == 1


@pytest.mark.django_db
class TestCartErrorFormat:
    """قالب یکسان خطا"""

    def test_stock_error_uses_standard_format(self, customer_client, product):
        response = _add(customer_client, product, product.stock + 1)

        assert response.status_code == 400
        assert response.data['success'] is False
        assert response.data['error']['code'] == 'business_rule_violation'
        assert str(product.stock) in response.data['error']['message']
