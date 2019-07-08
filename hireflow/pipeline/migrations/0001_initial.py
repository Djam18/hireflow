from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('candidates', '0001_initial'),
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(
                    choices=[('NEW', 'New'), ('SCREENING', 'Screening'), ('INTERVIEW', 'Interview'),
                             ('OFFER', 'Offer'), ('HIRED', 'Hired'), ('REJECTED', 'Rejected')],
                    default='NEW', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications', to='candidates.Candidate')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications', to='jobs.Job')),
                ('updated_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='updated_applications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('candidate', 'job')},
        ),
        migrations.CreateModel(
            name='StageHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_stage', models.CharField(max_length=20)),
                ('to_stage', models.CharField(max_length=20)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='history', to='pipeline.Application')),
                ('changed_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
