# Generated by Django 4.2.3 on 2023-07-09 06:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0004_rename_from_chat_group_chatmessage_chat_group_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ChatGroupInvite",
        ),
    ]
