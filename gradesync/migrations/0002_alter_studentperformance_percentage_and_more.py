# Generated by Django 5.1.1 on 2025-01-27 16:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gradesync", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentperformance",
            name="percentage",
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name="studentperformance",
            name="sgpa",
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name="studentperformance",
            name="total",
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name="SubjectMetrics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "avg_score",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("num_backlogs", models.IntegerField(default=0)),
                (
                    "pass_percentage",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "fail_percentage",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "absent_percentage",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("fcd_count", models.IntegerField(default=0)),
                ("fc_count", models.IntegerField(default=0)),
                ("sc_count", models.IntegerField(default=0)),
                ("fail_count", models.IntegerField(default=0)),
                ("absent_count", models.IntegerField(default=0)),
                ("highest_score", models.IntegerField(default=0)),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gradesync.section",
                    ),
                ),
                (
                    "semester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gradesync.semester",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gradesync.subject",
                    ),
                ),
            ],
        ),
    ]
