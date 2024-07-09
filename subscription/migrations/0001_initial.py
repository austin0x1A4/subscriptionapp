# Generated by Django 5.0.6 on 2024-06-30 13:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comments', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField()),
                ('investment_duration', models.CharField(choices=[('1y', '1 year'), ('2y', '2 years'), ('4y', '4 years'), ('5y', '5 years'), ('6y', '6 years'), ('7y', '7 years'), ('8y', '8 years'), ('9y', '9 years'), ('10y', '10 years')], max_length=10)),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='investments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(editable=False, max_length=6, unique=True)),
                ('account_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]