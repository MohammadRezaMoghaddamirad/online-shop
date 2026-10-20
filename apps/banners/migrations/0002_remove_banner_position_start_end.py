from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['sort_order', '-created_at']},
        ),
        migrations.RemoveField(model_name='banner', name='position'),
        migrations.RemoveField(model_name='banner', name='start_at'),
        migrations.RemoveField(model_name='banner', name='end_at'),
    ]
