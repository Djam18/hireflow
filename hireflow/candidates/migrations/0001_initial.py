from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('linkedin_url', models.URLField(blank=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/%Y/%m/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
