from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PromoCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=300)),
                ('badge_text', models.CharField(blank=True, help_text='متن نشان کوچک روی کارت، مثلاً «۲۰٪ تخفیف»', max_length=50)),
                ('image', models.ImageField(upload_to='promo_cards/')),
                ('link_url', models.URLField(blank=True, max_length=500)),
                ('button_text', models.CharField(blank=True, max_length=50)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['sort_order', '-created_at'],
            },
        ),
    ]
