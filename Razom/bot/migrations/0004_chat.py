# Generated by Django 4.1.7 on 2023-04-25 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0003_remove_messages_select_help_or_my_requests"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chat_id", models.CharField(db_index=True, max_length=64)),
                (
                    "status",
                    models.PositiveIntegerField(
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
                        default=1,
                        verbose_name="chat status",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="bot.recipients",
                    ),
                ),
                (
                    "volunteer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="bot.volunteers",
                    ),
                ),
            ],
        ),
    ]
