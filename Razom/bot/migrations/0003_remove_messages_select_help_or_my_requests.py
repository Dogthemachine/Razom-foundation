# Generated by Django 4.1.7 on 2023-04-20 12:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0002_messages_alter_address_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="messages",
            name="select_help_or_my_requests",
        ),
    ]