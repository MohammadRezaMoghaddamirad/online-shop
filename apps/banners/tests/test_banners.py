"""
تست‌های بنرها
"""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.banners.models import Banner


def make_image(name='banner.png'):
    buf = io.BytesIO()
    Image.new('RGB', (20, 10), 'red').save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


@pytest.fixture(autouse=True)
def tmp_media(settings, tmp_path):
    """آپلود تست‌ها داخل پوشه موقت ذخیره شود، نه media پروژه"""
    settings.MEDIA_ROOT = tmp_path


def create_banner(**kwargs):
    data = dict(title='Sale', image=make_image())
    data.update(kwargs)
    return Banner.objects.create(**data)


@pytest.mark.django_db
class TestBanners:
    url = '/api/v1/banners/'

    def test_list_public_only_active(self, api_client):
        create_banner(title='live')
        create_banner(title='inactive', is_active=False)

        response = api_client.get(self.url)

        assert response.status_code == 200
        titles = [b['title'] for b in response.data['results']]
        assert titles == ['live']

    def test_admin_sees_all(self, admin_client):
        create_banner(title='live')
        create_banner(title='inactive', is_active=False)

        response = admin_client.get(self.url)

        assert response.data['count'] == 2

    def test_sort_order(self, api_client):
        create_banner(title='second', sort_order=2)
        create_banner(title='first', sort_order=1)

        response = api_client.get(self.url)

        titles = [b['title'] for b in response.data['results']]
        assert titles == ['first', 'second']

    def test_create_as_admin(self, admin_client):
        response = admin_client.post(self.url, {
            'title': 'New banner',
            'image': make_image(),
            'link_url': 'https://example.com/sale',
        }, format='multipart')

        assert response.status_code == 201
        assert response.data['title'] == 'New banner'
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
        banner = create_banner()

        response = admin_client.patch(
            f'{self.url}{banner.id}/', {'is_active': False}
        )

        assert response.status_code == 200
        assert api_client.get(self.url).data['count'] == 0

    def test_delete_as_admin(self, admin_client):
        banner = create_banner()

        response = admin_client.delete(f'{self.url}{banner.id}/')

        assert response.status_code == 204
