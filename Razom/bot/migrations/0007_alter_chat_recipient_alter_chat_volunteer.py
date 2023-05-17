# Generated by Django 4.1.7 on 2023-05-16 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0006_recipients_address_alter_chat_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="recipient",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="bot.recipients",
            ),
        ),
        migrations.AlterField(
            model_name="chat",
            name="volunteer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="bot.volunteers",
            ),
        ),
    ]