from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='banners/')),
                ('link_url', models.URLField(blank=True, max_length=500)),
                ('position', models.CharField(choices=[('home_main', 'Home main'), ('home_side', 'Home side'), ('category', 'Category')], default='home_main', max_length=20)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('end_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['position', 'sort_order', '-created_at'],
            },
        ),
    ]
