# Generated by Django 4.1.5 on 2023-02-02 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('writing', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='writer',
            new_name='user',
        ),
    ]
