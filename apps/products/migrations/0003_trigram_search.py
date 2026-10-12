from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_brand'),
    ]

    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name='product',
            index=GinIndex(
                fields=['name'],
                opclasses=['gin_trgm_ops'],
                name='product_name_trgm_idx',
            ),
        ),
    ]