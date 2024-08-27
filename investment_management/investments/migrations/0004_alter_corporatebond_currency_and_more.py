# Generated by Django 5.0.6 on 2024-07-10 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0003_alter_governmentbondprimary_bond_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corporatebond',
            name='currency',
            field=models.CharField(choices=[('zmw', 'ZMW'), ('usd', 'USD')], default='zmw', max_length=3),
        ),
        migrations.AlterField(
            model_name='governmentbondprimary',
            name='currency',
            field=models.CharField(choices=[('zmw', 'ZMW'), ('usd', 'USD')], default='ZMW', max_length=3),
        ),
    ]
