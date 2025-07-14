from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0006_action_user_message'),
    ]

    operations = [
        TrigramExtension(),
    ]
