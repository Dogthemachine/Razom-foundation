# Generated by Django 4.1.7 on 2023-05-02 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0005_alter_chat_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipients",
            name="address",
            field=models.CharField(default="", max_length=300),
        ),
        migrations.AlterField(
            model_name="chat",
            name="status",
            field=models.PositiveIntegerField(
                choices=[
                    (2, "Starting registration"),
                    (3, "Print your phone"),
                    (4, "Print your firstname and surname"),
                    (5, "Print your date of birthday"),
                    (7, "Print your email, if you have"),
                    (8, "Registration is complete"),
                    (9, "Need help or my requests"),
                    (10, "List of requests"),
                    (11, "Request was deleted"),
                    (1, "Welcome message"),
                    (12, "Select category"),
                    (13, "Food categories"),
                    (14, "Print repair budget"),
                    (15, "Upload photo"),
                    (16, "Print your comment"),
                    (17, "Request is saved "),
                    (18, "Send request status massage"),
                    (19, "Send help request message"),
                ],
                default=1,
                verbose_name="chat status",
            ),
        ),
    ]
