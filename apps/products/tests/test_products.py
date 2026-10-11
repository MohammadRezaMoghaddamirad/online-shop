"""
تست‌های محصولات
"""
import pytest


@pytest.mark.django_db
class TestProducts:
    """تست API محصولات"""

    list_url = '/api/v1/products/'

    def test_list_products_public(self, api_client, product):
        """لیست محصولات برای همه"""
        response = api_client.get(self.list_url)

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'iPhone 15'

    def test_product_detail(self, api_client, product):
        """جزئیات محصول"""
        response = api_client.get(f'{self.list_url}{product.id}/')

        assert response.status_code == 200
        assert response.data['name'] == 'iPhone 15'

    def test_create_product_as_admin(self, admin_client, category):
        """ساخت محصول توسط ادمین"""
        response = admin_client.post(self.list_url, {
            'name': 'Samsung S24',
            'description': 'گوشی سامسونگ',
            'price': 40000000,
            'category_id': category.id,
            'stock': 5,
            'is_active': True
        })

        assert response.status_code == 201
        assert response.data['name'] == 'Samsung S24'

    def test_create_product_as_customer_forbidden(self, customer_client, category):
        """ساخت محصول توسط کاربر عادی — خطا"""
        response = customer_client.post(self.list_url, {
            'name': 'Samsung S24',
            'price': 40000000,
            'category_id': category.id,
            'stock': 5
        })

        assert response.status_code == 403

    def test_update_stock(self, admin_client, product):
        """ویرایش موجودی"""
        response = admin_client.patch(
            f'{self.list_url}{product.id}/stock/',
            {'stock': 25}
        )

        assert response.status_code == 200
        assert response.data['stock'] == 25

    def test_inactive_product_hidden(self, api_client, product):
        """محصول غیرفعال نمایش داده نمی‌شود"""
        product.is_active = False
        product.save()

        response = api_client.get(self.list_url)

        assert response.status_code == 200
        assert response.data['count'] == 0