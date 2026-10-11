"""
تست‌های برندها
"""
import pytest

from apps.brands.models import Brand
from apps.products.models import Product


@pytest.fixture
def brand(db):
    return Brand.objects.create(name='Apple', is_active=True)


@pytest.mark.django_db
class TestBrands:
    url = '/api/v1/brands/'

    def test_list_public(self, api_client, brand):
        response = api_client.get(self.url)

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Apple'

    def test_inactive_hidden_from_customer_but_visible_to_admin(
        self, customer_client, admin_client, brand
    ):
        Brand.objects.create(name='OldBrand', is_active=False)

        assert customer_client.get(self.url).data['count'] == 1
        assert admin_client.get(self.url).data['count'] == 2

    def test_create_as_admin(self, admin_client):
        response = admin_client.post(self.url, {'name': 'Samsung'})

        assert response.status_code == 201
        assert response.data['name'] == 'Samsung'

    def test_create_as_customer_forbidden(self, customer_client):
        response = customer_client.post(self.url, {'name': 'Samsung'})

        assert response.status_code == 403

    def test_duplicate_name_rejected(self, admin_client, brand):
        response = admin_client.post(self.url, {'name': 'Apple'})

        assert response.status_code == 400

    def test_delete_empty_brand(self, admin_client, brand):
        response = admin_client.delete(f'{self.url}{brand.id}/')

        assert response.status_code == 204

    def test_delete_brand_with_products_returns_409(
        self, admin_client, brand, category
    ):
        Product.objects.create(
            name='iPhone', price=1000, category=category, brand=brand, stock=1
        )

        response = admin_client.delete(f'{self.url}{brand.id}/')

        assert response.status_code == 409
        assert response.data['error']['code'] == 'protected'


@pytest.mark.django_db
class TestProductBrand:
    def test_create_product_with_brand(self, admin_client, category, brand):
        response = admin_client.post('/api/v1/products/', {
            'name': 'iPhone 15',
            'price': 50000000,
            'category_id': category.id,
            'brand_id': brand.id,
            'stock': 3,
        })

        assert response.status_code == 201
        assert response.data['brand']['name'] == 'Apple'

    def test_create_product_without_brand_still_works(self, admin_client, category):
        response = admin_client.post('/api/v1/products/', {
            'name': 'No brand',
            'price': 1000,
            'category_id': category.id,
            'stock': 1,
        })

        assert response.status_code == 201
        assert response.data['brand'] is None

    def test_filter_products_by_brand(self, api_client, category, brand):
        Product.objects.create(
            name='iPhone', price=1000, category=category, brand=brand, stock=1
        )
        Product.objects.create(
            name='Other', price=1000, category=category, stock=1
        )

        response = api_client.get(f'/api/v1/products/?brand={brand.id}')

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['brand_name'] == 'Apple'
