from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_candidate_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
