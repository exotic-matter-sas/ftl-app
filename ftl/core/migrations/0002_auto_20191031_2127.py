#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

# Generated by Django 2.2.5 on 2019-10-31 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ftldocument',
            name='language',
            field=models.CharField(default='simple', max_length=64),
        ),
    ]
