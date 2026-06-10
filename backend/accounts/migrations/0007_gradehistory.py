from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0006_profile_grade_tokens'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('detection', models.FloatField(default=0)),
                ('confidence', models.FloatField(default=0)),
                ('stage', models.CharField(blank=True, max_length=24)),
                ('result_json', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='gradehistory',
            index=models.Index(fields=['user', '-created_at'], name='accounts_gr_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='gradehistory',
            index=models.Index(fields=['topic'], name='accounts_gr_topic_idx'),
        ),
        migrations.AddIndex(
            model_name='gradehistory',
            index=models.Index(fields=['-created_at'], name='accounts_gr_created_idx'),
        ),
    ]
