# Generated by Django 4.1.7 on 2023-05-18 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0007_alter_chat_recipient_alter_chat_volunteer"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subcategories",
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
                ("name", models.CharField(default="", max_length=70)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="bot.recipients",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subcategories",
                "verbose_name_plural": "Subcategories",
            },
        ),
        migrations.AddField(
            model_name="requests",
            name="subcategory",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="bot.subcategories",
            ),
        ),
    ]
