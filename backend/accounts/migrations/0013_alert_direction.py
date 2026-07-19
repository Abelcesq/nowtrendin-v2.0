# Falls-below alerts (mobile-board deferred item, founder-ordered 2026-07-19).
# Additive with default 'above' — every existing alert keeps its exact behavior.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alert_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='direction',
            field=models.CharField(
                choices=[('above', 'above'), ('below', 'below')],
                default='above', max_length=6),
        ),
    ]
