# Generated by Django 4.1.5 on 2023-02-13 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writing', '0011_remove_sentence_day_of_the_week'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='bool_like_users',
        ),
        migrations.AddField(
            model_name='sentence',
            name='day_of_the_week',
            field=models.CharField(max_length=10, null=True),
        ),
    ]