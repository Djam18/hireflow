from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pipeline', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_type', models.CharField(
                    choices=[('PHONE', 'Phone Screen'), ('TECHNICAL', 'Technical'),
                             ('BEHAVIORAL', 'Behavioral'), ('FINAL', 'Final Round')],
                    default='PHONE', max_length=20)),
                ('scheduled_at', models.DateTimeField()),
                ('duration_minutes', models.IntegerField(default=60)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='interviews', to='pipeline.Application')),
                ('interviewer', models.ForeignKey(null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='interviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
