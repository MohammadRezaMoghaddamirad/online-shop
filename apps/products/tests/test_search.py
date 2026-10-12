"""
تست‌های جست‌وجوی محصولات (pg_trgm)
"""
import pytest

from apps.products.models import Product


@pytest.fixture
def phones(db, category):
    def make(name):
        return Product.objects.create(
            name=name, price=1000, category=category, stock=5, is_active=True
        )
    return make('Samsung'), make('Xiaomi')


@pytest.mark.django_db
class TestProductSearch:
    url = '/api/v1/products/'

    def test_typo_is_tolerated(self, api_client, phones):
        response = api_client.get(f'{self.url}?search=Samsug')

        names = [p['name'] for p in response.data['results']]
        assert names == ['Samsung']

    def test_substring_still_works(self, api_client, phones):
        response = api_client.get(f'{self.url}?search=sams')

        names = [p['name'] for p in response.data['results']]
        assert 'Samsung' in names

    def test_unrelated_term_returns_nothing(self, api_client, phones):
        response = api_client.get(f'{self.url}?search=zzzzzz')

        assert response.data['count'] == 0

    def test_empty_search_returns_all(self, api_client, phones):
        response = api_client.get(f'{self.url}?search=')

        assert response.data['count'] == 2