# Generated by Django 3.2.16 on 2024-06-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='blogicum_images', verbose_name='Фото'),
        ),
    ]