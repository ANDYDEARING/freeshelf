# Generated by Django 2.2.2 on 2019-06-28 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0012_book_times_favorited'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='Enter your comment (1000 chars max).', max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Book')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
