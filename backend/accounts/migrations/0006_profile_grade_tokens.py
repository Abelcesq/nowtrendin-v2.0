from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_reset_code_profile_reset_expires'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='grade_tokens',
            field=models.IntegerField(default=0),
        ),
    ]
