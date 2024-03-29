# Generated by Django 4.2.6 on 2024-01-22 13:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("my_site", "0006_alter_post_job_datepost"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apply_job",
            name="resume",
            field=models.FileField(default="", upload_to="my_site/resume"),
        ),
        migrations.AlterField(
            model_name="post_job",
            name="datepost",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
