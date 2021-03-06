# Generated by Django 3.0.7 on 2020-08-01 06:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order_api', '0006_auto_20200729_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('p', 'Placed'), ('a', 'Acknowledged'), ('r', 'Ready'), ('t', 'In Transit'), ('w', 'Delivered'), ('e', 'Returned'), ('s', 'No Stock (P)'), ('X', 'No Stock'), ('d', 'Dismissed')], default='p', max_length=1),
        ),
        migrations.CreateModel(
            name='OrderActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prev_status', models.CharField(choices=[('p', 'Placed'), ('a', 'Acknowledged'), ('r', 'Ready'), ('t', 'In Transit'), ('w', 'Delivered'), ('e', 'Returned'), ('s', 'No Stock (P)'), ('X', 'No Stock'), ('d', 'Dismissed')], max_length=1)),
                ('next_status', models.CharField(choices=[('p', 'Placed'), ('a', 'Acknowledged'), ('r', 'Ready'), ('t', 'In Transit'), ('w', 'Delivered'), ('e', 'Returned'), ('s', 'No Stock (P)'), ('X', 'No Stock'), ('d', 'Dismissed')], max_length=1)),
                ('changed_on', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order_api.Order')),
            ],
        ),
    ]
