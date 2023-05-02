# Generated by Django 4.1.7 on 2023-04-27 09:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0004_chat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="status",
            field=models.PositiveIntegerField(
                choices=[
                    (1, "Starting registration"),
                    (2, "Print your phone"),
                    (3, "Print your firstname and surname"),
                    (4, "Print your date of birthday"),
                    (5, "Print your email, if you have"),
                    (6, "Registration is complete"),
                    (7, "Need help or my requests"),
                    (8, "List of requests"),
                    (9, "Request was deleted"),
                    (10, "Welcome message"),
                    (11, "Select category"),
                    (12, "Food categories"),
                    (13, "Print repair budget"),
                    (14, "Upload photo"),
                    (15, "Print your comment"),
                    (16, "Request is saved "),
                    (17, "Send request status massage"),
                    (18, "Send help request message"),
                ],
                default=10,
                verbose_name="chat status",
            ),
        ),
    ]