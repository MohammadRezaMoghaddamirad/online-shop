"""
تست‌های کارت‌های تبلیغاتی
"""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.promo_cards.models import PromoCard


def make_image(name='promo.png'):
    buf = io.BytesIO()
    Image.new('RGB', (20, 10), 'blue').save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


@pytest.fixture(autouse=True)
def tmp_media(settings, tmp_path):
    """آپلود تست‌ها داخل پوشه موقت ذخیره شود، نه media پروژه"""
    settings.MEDIA_ROOT = tmp_path


def create_card(**kwargs):
    data = dict(title='Summer', image=make_image())
    data.update(kwargs)
    return PromoCard.objects.create(**data)


@pytest.mark.django_db
class TestPromoCards:
    url = '/api/v1/promo-cards/'

    def test_list_public_only_active(self, api_client):
        create_card(title='live')
        create_card(title='inactive', is_active=False)

        response = api_client.get(self.url)

        assert response.status_code == 200
        assert [c['title'] for c in response.data['results']] == ['live']

    def test_admin_sees_all(self, admin_client):
        create_card(title='live')
        create_card(title='inactive', is_active=False)

        assert admin_client.get(self.url).data['count'] == 2

    def test_sort_order(self, api_client):
        create_card(title='second', sort_order=2)
        create_card(title='first', sort_order=1)

        response = api_client.get(self.url)

        assert [c['title'] for c in response.data['results']] == ['first', 'second']

    def test_create_as_admin(self, admin_client):
        response = admin_client.post(self.url, {
            'title': 'Big sale',
            'subtitle': 'تا ۵۰٪ تخفیف',
            'badge_text': '۵۰٪',
            'button_text': 'خرید کنید',
            'image': make_image(),
            'link_url': 'https://example.com/sale',
        }, format='multipart')

        assert response.status_code == 201
        assert response.data['badge_text'] == '۵۰٪'
        assert response.data['is_active'] is True

    def test_create_as_customer_forbidden(self, customer_client):
        response = customer_client.post(self.url, {
            'title': 'x', 'image': make_image(),
        }, format='multipart')

        assert response.status_code == 403

    def test_create_without_image_rejected(self, admin_client):
        response = admin_client.post(self.url, {'title': 'x'}, format='multipart')

        assert response.status_code == 400
        assert 'image' in response.data['error']['details']

    def test_patch_deactivate_hides_from_public(self, admin_client, api_client):
        card = create_card()

        response = admin_client.patch(f'{self.url}{card.id}/', {'is_active': False})

        assert response.status_code == 200
        assert api_client.get(self.url).data['count'] == 0

    def test_delete_as_admin(self, admin_client):
        card = create_card()

        assert admin_client.delete(f'{self.url}{card.id}/').status_code == 204
