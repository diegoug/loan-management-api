# Generated by Django 5.0.6 on 2024-06-01 14:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=60, unique=True)),
                ('status', models.SmallIntegerField(choices=[(1, 'Active'), (2, 'Inactive')])),
                ('score', models.DecimalField(decimal_places=2, max_digits=12)),
                ('preapproved_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=60, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.SmallIntegerField(choices=[(1, 'Pending'), (2, 'Active'), (3, 'Rejected'), (4, 'Paid')], default=1)),
                ('contract_version', models.CharField(blank=True, max_length=30, null=True)),
                ('maximum_payment_date', models.DateTimeField()),
                ('taken_at', models.DateTimeField(blank=True, null=True)),
                ('outstanding', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=60, unique=True)),
                ('total_amount', models.DecimalField(decimal_places=10, max_digits=20)),
                ('status', models.SmallIntegerField(choices=[(1, 'Completed'), (2, 'Rejected')])),
                ('paid_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.customer')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=10, max_digits=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.loan')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.payment')),
            ],
        ),
    ]
